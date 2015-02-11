import datetime as dt
# Third-party imports
from google.appengine.api.app_identity import get_application_id
from google.appengine.ext import db


SESSION_LIFETIME = 1  # day
GLOBAL_PARENT = db.Key.from_path('app', get_application_id())


class SimpleProjection(object):
    def __init__(self, entity):
        self.entity = entity

    def __getattr__(self, item):
        return getattr(self.entity, item)

    def __repr__(self):
        return '[Projection of {}]'.format(repr(self.entity))


class BaseModel(db.Model):
    @classmethod
    def by_prop(cls, prop_name, value, ancestor=GLOBAL_PARENT):
        q = cls.all().ancestor(ancestor).filter('{} ='.format(prop_name), value)

        return q.get()


class User(BaseModel):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True, indexed=False)
    email = db.EmailProperty(required=False)


class Session(BaseModel):
    sid = db.StringProperty(required=True)
    user = db.ReferenceProperty(User, collection_name="Sessions")
    created = db.DateTimeProperty(auto_now_add=True)
    logout_url = db.StringProperty(default='/')

    def has_expired(self):
        delta = dt.datetime.now() - self.created
        return delta.days > SESSION_LIFETIME


class Article(BaseModel):
    url = db.StringProperty(required=True)

    def new_version(self, head, body):
        version = Version(
            article=self, head=head, body=body, parent=GLOBAL_PARENT)
        version.put()

    def project(self, version):
        projection = SimpleProjection(self)
        projection.url = self.url
        projection.head = version.head
        projection.body = version.body
        projection.modified = version.created

        return projection

    @classmethod
    def latest_version(cls, url):
        article = cls.by_prop('url', url)
        if article is not None:
            version = article.version_set.order('-created').get()
            if version is not None:
                return article.project(version)

    @classmethod
    def new(cls, url, head, body):
        article = cls(url=url, parent=GLOBAL_PARENT)
        article.put()
        first_version = Version(
            article=article, head=head, body=body, parent=GLOBAL_PARENT)
        first_version.put()
        return article.project(first_version)


class Version(BaseModel):
    article = db.ReferenceProperty(Article, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    head = db.StringProperty(required=True)
    body = db.TextProperty()