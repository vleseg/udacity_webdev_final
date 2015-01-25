# --coding:utf-8--
import re
# Third-party imports
import webapp2
# Project-specific imports
from forms import EditForm, LoginForm, SignupForm
from hashutils import check_against_hash, encrypt, make_hash, make_salt
from jinjacfg import jinja_environment
from model import GLOBAL_PARENT, User, Session, WikiPage

# Setup logging
import logging
logging.getLogger().setLevel(logging.DEBUG)


# Handlers
class BaseHandler(webapp2.RequestHandler):
    template = ""

    def __init__(self, request=None, response=None):
        self.session = None
        self.user = None
        self.context = {}

        super(BaseHandler, self).__init__(request, response)

    # Auth methods
    def sid_is_valid(self):
        sid = self.request.cookies.get("sid")
        if sid:
            self.session = Session.by_prop('sid', sid)
            if self.session and not self.session.has_expired():
                return True

    def get(self, *args, **kwargs):
        self.auth_wrapper(self._get, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.auth_wrapper(self._post, *args, **kwargs)

    def handle_exception(self, exception, debug):
        self.auth_wrapper(self._handle_exception, exception, debug)

    def auth_wrapper(self, method, *args, **kwargs):
        if self.sid_is_valid():
            self.user = self.session.user
        method(*args, **kwargs)

    # Actual handlers
    def _get(self, *args, **kwargs):
        raise NotImplementedError

    def _post(self, *args, **kwargs):
        raise NotImplementedError

    def _handle_exception(self, exception, debug):
        super(BaseHandler, self).handle_exception(exception, debug)

    # Render & write methods
    @staticmethod
    def render_str(template, **context):
        t = jinja_environment.get_template(template)
        return t.render(context)

    def render(self):
        self.write(self.render_str(self.template, **self.context))

    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def redirect_with_cookie(self, path, new_cookies):
        for k in self.request.cookies:
            if k not in new_cookies:
                self.response.delete_cookie(k)
        for key, value in new_cookies.items():
            self.response.set_cookie(key, value)
        self.redirect(str(path))


# Base handler for signup & login pages
class AuthPageHandler(BaseHandler):
    def auth_wrapper(self, method, *args, **kwargs):
        method(*args, **kwargs)

    # It won't set 'self.session', 'cause it is used exclusively by signup
    # and login handlers, that die after user has been authenticated
    @staticmethod
    def get_new_session_cookie(user):
        sid = encrypt(user.name + user.password_hash + make_salt())
        session = Session(sid=sid, user=user, parent=GLOBAL_PARENT)
        session.put()
        return {'sid': sid}


# Signup form regexps
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")


class SignupPage(AuthPageHandler):
    # TODO: line up form fields and labels nicely
    # TODO: error messages should not shift submit button to alt link to side
    template = "auth/signup.html"

    def _get(self):
        self.context['form'] = SignupForm()
        self.render()

    def _post(self):
        form = SignupForm(self.request.params)

        redirect_path = self.request.cookies.get('referrer', '/')

        if form.validate():
            username = form.username.data
            pwd = form.password.data
            pwd_hash = make_hash(username + pwd)

            user = User(name=username, password_hash=pwd_hash,
                        parent=GLOBAL_PARENT)
            if form.email.data:
                user.email = form.email.data
            user.put()

            self.redirect_with_cookie(
                redirect_path, self.get_new_session_cookie(user))
        else:
            form.password.data = ''
            form.verify.data = ''
            self.context['form'] = form
            self.render()


class LoginPage(AuthPageHandler):
    # TODO: use wtforms
    # TODO: errors have to appear under form
    template = "auth/login.html"

    def _get(self):
        self.context['form'] = LoginForm()
        self.render()

    def _post(self):
        form = LoginForm(self.request.params)
        redirect_path = self.request.cookies.get('referrer', '/')

        if form.validate():
            self.redirect_with_cookie(
                redirect_path, self.get_new_session_cookie(form._user))
        else:
            form.password.data = ''
            self.context['form'] = form
            self.render()


class Logout(BaseHandler):
    def _get(self):
        if self.session:
            self.session.delete()
        self.redirect_with_cookie('/', {})


class WikiViewPage(BaseHandler):
    template = "wiki/view_page.html"

    def _handle_exception(self, exception, debug):
        self.template = "wiki/error.html"

        if exception.status_int == 404:
            self.context = {
                'user': self.user,
                'error': 'Page not found'
            }
            self.response.set_status(404)
        else:
            super(WikiViewPage, self)._handle_exception(exception, debug)

        self.render()

    def _get(self, path):
        page = WikiPage.by_prop('url', path)
        if page is None:
            if path == '/':
                default_body = (
                    '<p>You are free to create new pages and edit existing '
                    'ones.</p>')
                page = WikiPage(
                    url='/', body=default_body, title='Welcome to MyWiki!',
                    parent=GLOBAL_PARENT)
                page.put()
            elif self.user is None:
                self.abort(404)
            else:
                self.redirect('/_edit' + path, abort=True)
        self.context = {'page': page, 'user': self.user}
        self.render()


class WikiEditPage(BaseHandler):
    template = "wiki/edit_page.html"

    def _get(self, path):
        if self.user is None:
            self.redirect_with_cookie('/login', {'referrer': self.request.url})

        form = EditForm()
        page = WikiPage.by_prop('url', path)

        if page is None:
            if path == '/':
                form.title.data = 'Welcome to MyWiki!'
                form.body.data = (
                    '<p>You are free to create new pages and edit existing '
                    'ones.</p>')
        else:
            form.title.data = page.title
            form.body.data = page.body
        self.context = {'user': self.user, 'form': form, 'page_url': path}
        self.render()

    def _post(self, path):
        if self.user is None:
            self.redirect('/login', abort=True)

        form = EditForm(self.request.params)
        page = WikiPage.by_prop('url', path)
        if page is None:
            page = WikiPage(
                url=path, title=form.title.data, parent=GLOBAL_PARENT)
        page.body = form.body.data
        page.put()

        self.redirect(path)


PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
handlers = [
    ('/signup', SignupPage),
    ('/login', LoginPage),
    ('/logout', Logout),
    ('/_edit' + PAGE_RE, WikiEditPage),
    (PAGE_RE, WikiViewPage)
]
app = webapp2.WSGIApplication(handlers, debug=True)
