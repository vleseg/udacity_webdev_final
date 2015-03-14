# --coding:utf-8--
import re
# Third-party imports
import webapp2
# Project-specific imports
from forms import EditForm, LoginForm, SignupForm
from hashutils import encrypt, make_hash, make_salt
from jinjacfg import jinja_environment, resolve_msg_from_errtype
from model import GLOBAL_PARENT, User, Session, Article, Version

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
        mode_to_title = {
            'new': 'New Article', 'signup': 'Sign Up', 'login': 'Login',
            'view': lambda c: c['article'].head,
            'edit': lambda c: '{} (edit)'.format(c['article'].head),
            'history': lambda c: '{} (history)'.format(c['article'].head),
            'error': lambda c: resolve_msg_from_errtype(c['error_type'])
        }
        mode = self.context['mode']
        sep = u'—' if mode in ['view', 'edit', 'history'] else '***'
        title_handler = mode_to_title[mode]
        if callable(title_handler):
            self.context['title'] = u'MyWiki {0} {1}'.format(
                sep, title_handler(self.context))
        else:
            self.context['title'] = u'MyWiki {0} {1}'.format(sep, title_handler)

    def render_regular_not_found(self):
        self.template = 'wiki/error.html'
        self.context.update(
            {'mode': 'error', 'error_type': 'not_found', 'logout_url': '/'})
        self.response.set_status(404)
        self.render()

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
        self.context['mode'] = 'signup'
        super(SignupPage, self).dispatch()

    def _get(self):
        return_to = self.request.get('return_to')
        if return_to:
            self.response.set_cookie('referrer', return_to)

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
        self.context['mode'] = 'login'
        super(LoginPage, self).dispatch()

    def _get(self):
        return_to = self.request.get('return_to')
        if return_to:
            self.response.set_cookie('referrer', return_to)

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


class ViewPage(BaseHandler):
    template = "wiki/view_page.html"

    def dispatch(self):
        self.context.update({'mode': 'view', 'logout_url': self.request.url})
        super(ViewPage, self).dispatch()

    def _handle_exception(self, exception, debug):
        if exception.status_int == 404:
            self.render_regular_not_found()
        else:
            super(ViewPage, self)._handle_exception(exception, debug)

    def _get(self, url, version=None):
        if version is None:
            article = Article.by_url(url)
        else:
            article = Article.by_url(url, version)
        if article is None:
            if url == '/':
                default_body = (
                    '<p>You are free to create new articles and edit existing '
                    'ones.</p>')
                article = Article.new(
                    url='/', body=default_body, head='Welcome to MyWiki!')
            elif self.user is None:
                self.context['url'] = url
                self.abort(404)
            else:
                self.redirect('/_edit' + url, abort=True)
        self.context.update({'article': article, 'user': self.user})

        self.render()


class HistoryPage(BaseHandler):
    template = "wiki/history.html"

    def dispatch(self):
        self.context.update(
            {'mode': 'history', 'logout_url': self.request.url})
        super(HistoryPage, self).dispatch()

    def _handle_exception(self, exception, debug):
        if exception.status_int == 404:
            self.render_regular_not_found()
        else:
            super(HistoryPage, self)._handle_exception(exception, debug)

    def _get(self, url):
        article = Article.by_url(url)
        if article is None:
            if self.user is None:
                self.abort(404)
            else:
                self.redirect('/_edit' + url, abort=True)

        self.context.update({'article': article, 'user': self.user})
        self.render()


class EditPage(BaseHandler):
    template = "wiki/edit_page.html"

    def dispatch(self):
        self.context.update(
            {'mode': 'edit',
             'logout_url': self.request.url.split('_edit')[-1]})
        super(EditPage, self).dispatch()

    @staticmethod
    def form_head_from_path(path):
        words = path.strip('/').split('_')
        return ' '.join([w.capitalize() for w in words])

    def _get(self, url, version=None):
        if self.user is None:
            self.redirect_with_cookie('/login', {'referrer': self.request.url})
        form = EditForm()
        if version is None:
            article = Article.by_url(url)
        else:
            article = Article.by_url(url, version)

        if article is None:
            if url == '/':
                default_body = (
                    '<p>You are free to create new articles and edit existing '
                    'ones.</p>')
                article = Article.new(
                    url='/', body=default_body, head='Welcome to MyWiki!')
            else:
                self.context.update({'mode': 'new', 'logout_url': '/'})
                form.head.data = self.form_head_from_path(url)
        else:
            form.head.data = article.head
            form.body.data = article.body

        self.context.update(
            {'form': form, 'article': article, 'user': self.user})
        self.render()

    def _post(self, url, version=None):
        if self.user is None:
            self.redirect('/login', abort=True)

        form = EditForm(self.request.params)
        if version is None:
            article = Article.by_url(url)
        else:
            article = Article.by_url(url, version)

        if article is None:
            self.context['mode'] = 'new'

        if form.validate():
            if self.context['mode'] == 'new':
                Article.new(url, form.head.data, form.body.data)
            else:
                article.new_version(form.head.data, form.body.data)
            self.redirect(url)
        else:
            self.context.update(
                {'user': self.user, 'form': form, 'article': article})
            self.render()


class DeleteVersion(BaseHandler):
    def _handle_exception(self, exception, debug):
        self.template = "wiki/error.html"

        self.response.set_status(exception.status_int)
        self.context.update({'mode': 'error', 'user': self.user})
        if exception.status_int == 403:
            self.context.update({
                'error_type': 'sole_version_del_attempt', 'logout_url': '/'
            })
        elif exception.status_int == 404:
            error_type = 'not_found_dv'
            if self.context.pop('article_exists', False):
                error_type = 'version_not_found'
            self.context.update({
                'error_type': error_type, 'logout_url': '/'
            })
        else:
            super(DeleteVersion, self)._handle_exception(exception, debug)

        self.render()

    def _get(self, url, version_id):
        if not self.user:
            pass
        else:
            article = Article.by_url(url, project_with_version=False)
            if article is None:
                self.context['url'] = url
                self.abort(404)

            version = Version.by_id(int(version_id))

            if version is None or not version.belongs_to_article(article):
                self.context['article_exists'] = True
                self.abort(404)

            # If it is article's sole version.
            if version.is_first() and version.is_latest():
                self.abort(403)
            version.delete()
            self.redirect(url)


ARTICLE_RE = r'((?:/[a-zA-Z0-9_-]*)+?)/?'
handlers = [
    (r'/signup', SignupPage),
    (r'/login', LoginPage),
    (r'/logout', Logout),
    (r'/_delete' + ARTICLE_RE + r'_version/' + r'(\d+)', DeleteVersion),
    (r'/_edit' + ARTICLE_RE + r'_version/' + r'(\d+)', EditPage),
    (r'/_edit' + ARTICLE_RE, EditPage),
    (r'/_history' + ARTICLE_RE, HistoryPage),
    (ARTICLE_RE + r'_version/' + r'(\d+)', ViewPage),
    (ARTICLE_RE, ViewPage)
]
app = webapp2.WSGIApplication(handlers, debug=True)