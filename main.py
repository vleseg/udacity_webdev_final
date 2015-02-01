# --coding:utf-8--
import re
# Third-party imports
import webapp2
# Project-specific imports
from forms import EditForm, LoginForm, SignupForm
from hashutils import encrypt, make_hash, make_salt
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

    def dispatch(self):
        super(BaseHandler, self).dispatch()
        # logout_url must be initially set in overriding class; it may change
        # inside handling method.
        try:
            self.set_logout_url(self.context['logout_url'])
        except KeyError:  # no logout_url was defined, will use the default
            pass

    def get(self, *args, **kwargs):
        self.auth_wrapper(self._get, *args, **kwargs)

    def post(self, *args, **kwargs):
        self.auth_wrapper(self._post, *args, **kwargs)

    def handle_exception(self, exception, debug):
        # Correctly handle all internal server errors.
        if not isinstance(exception, webapp2.HTTPException):
            super(BaseHandler, self).handle_exception(exception, debug)
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
    def set_title(self):
        state_to_title = {
            'new': 'New Page', 'signup': 'Sign Up', 'login': 'Login',
            'edit': lambda c: '{} (edit)'.format(c['page'].head),
            'view': lambda c: c['page'].head,
            'error': lambda c: c['error']
        }
        state = self.context['state']
        sep = u'—' if state in ['view', 'edit'] else '***'
        title_handler = state_to_title[state]
        if callable(title_handler):
            self.context['title'] = u'MyWiki {0} {1}'.format(
                sep, title_handler(self.context))
        else:
            self.context['title'] = u'MyWiki {0} {1}'.format(sep, title_handler)

    @staticmethod
    def render_str(template, **context):
        t = jinja_environment.get_template(template)
        return t.render(context)

    def render(self):
        self.set_title()
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

    def set_logout_url(self, url):
        try:
            self.session.logout_url = url
            self.session.put()
        except AttributeError:
            pass


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
    template = "auth/signup.html"

    def dispatch(self):
        self.context['state'] = 'signup'
        super(SignupPage, self).dispatch()

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
    template = "auth/login.html"

    def dispatch(self):
        self.context['state'] = 'login'
        super(LoginPage, self).dispatch()

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
        logout_url = self.session.logout_url
        if self.session:
            self.session.delete()
        self.redirect_with_cookie(logout_url, {})


class WikiViewPage(BaseHandler):
    template = "wiki/view_page.html"

    def dispatch(self):
        self.context.update({'state': 'view', 'logout_url': self.request.url})
        super(WikiViewPage, self).dispatch()

    def _handle_exception(self, exception, debug):
        self.template = "wiki/error.html"

        if exception.status_int == 404:
            self.context.update(
                {'error': 'Page not found', 'state': 'error',
                 'logout_url': '/'})
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
                    url='/', body=default_body, head='Welcome to MyWiki!',
                    parent=GLOBAL_PARENT)
                page.put()
            elif self.user is None:
                self.abort(404)
            else:
                self.redirect('/_edit' + path, abort=True)
        self.context.update({'page': page, 'user': self.user})

        self.render()


class WikiEditPage(BaseHandler):
    template = "wiki/edit_page.html"

    def dispatch(self):
        self.context.update(
            {'state': 'edit',
             'logout_url': self.request.url.split('_edit')[-1]})
        super(WikiEditPage, self).dispatch()

    @staticmethod
    def form_head_from_path(path):
        words = path.strip('/').split('_')
        return ' '.join([w.capitalize() for w in words])

    def _get(self, path):
        if self.user is None:
            self.redirect_with_cookie('/login', {'referrer': self.request.url})

        form = EditForm()
        page = WikiPage.by_prop('url', path)

        if page is None:
            if path == '/':
                default_body = (
                    '<p>You are free to create new pages and edit existing '
                    'ones.</p>')
                page = WikiPage(
                    url='/', body=default_body, head='Welcome to MyWiki!',
                    parent=GLOBAL_PARENT)
                page.put()
            else:
                self.context.update({'state': 'new', 'logout_url': '/'})
                form.head.data = self.form_head_from_path(path)
        else:
            form.head.data = page.head
            form.body.data = page.body

        self.context.update({'form': form, 'page': page, 'user': self.user})
        self.render()

    def _post(self, path):
        if self.user is None:
            self.redirect('/login', abort=True)

        form = EditForm(self.request.params)
        page = WikiPage.by_prop('url', path)
        if page is None:
            self.context['state'] = 'new'

        if form.validate():
            if self.context['state'] == 'new':
                page = WikiPage(
                    url=path, head=form.head.data, parent=GLOBAL_PARENT)
            page.head = form.head.data
            page.body = form.body.data
            page.put()
            self.redirect(path)
        else:
            self.context.update({'user': self.user, 'form': form, 'page': page})
            self.render()


PAGE_RE = r'(/(?:[a-zA-Z0-9_-]+/?)*)'
handlers = [
    ('/signup', SignupPage),
    ('/login', LoginPage),
    ('/logout', Logout),
    ('/_edit' + PAGE_RE, WikiEditPage),
    (PAGE_RE, WikiViewPage)
]
app = webapp2.WSGIApplication(handlers, debug=True)