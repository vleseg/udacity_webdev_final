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
    def __getattr__(self, item):
        if item == 'id':
            return self.key().id()
        raise AttributeError(item)

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
    # Reference class is not set, because Version class is defined lower in this
    # file and interpreter would not see it.
    # Both first_version and latest_version must actually be set to
    # required=True, but this is not done due to technical limitations.
    first_version = db.ReferenceProperty()
    # Collection name won't be used; this is to suppress DuplicatePropertyError.
    latest_version = db.ReferenceProperty(collection_name='_')
    url = db.StringProperty(required=True)

    def all_versions(self):
        q = self.version_set
        return q.order('-created')

    def new_version(self, head, body):
        version = Version(
            article=self, head=head, body=body, parent=GLOBAL_PARENT)
        version.put()

        self.latest_version = version
        self.put()

    def project(self, version):
        projection = SimpleProjection(self)
        projection.url = self.url
        projection.head = version.head
        projection.body = version.body
        projection.modified = version.created
        projection.version = version

        return projection

    def get_latest_version(self):
        return self.project(self.latest_version)

    def version_by_id(self, version_id):
        version = Version.get_by_id(int(version_id), parent=GLOBAL_PARENT)
        if version is not None:
            return self.project(version)

    @classmethod
    def by_url(cls, url, version=None):
        article = cls.by_prop('url', url)
        if article is not None:
            if version is None:
                return article.get_latest_version()
            else:
                p = article.version_by_id(version)
                return p if p is not None else article.get_latest_version()

    @classmethod
    @db.transactional
    def new(cls, url, head, body):
        article = cls(url=url, parent=GLOBAL_PARENT)
        article.put()

        first_version = Version(
            article=article, head=head, body=body, parent=GLOBAL_PARENT)
        first_version.put()

        article.first_version = first_version
        article.latest_version = first_version
        article.put()

        return article.project(first_version)


class Version(BaseModel):
    article = db.ReferenceProperty(Article, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    head = db.StringProperty(required=True)
    body = db.TextProperty()

    def delete(self):
        article = self.article
        is_latest = self.is_latest()
        is_first = self.is_first()
        super(Version, self).delete()
        if is_latest:
            new_latest = article.version_set.ancestor(
                GLOBAL_PARENT).order('-created').get()
            self.article.latest_version = new_latest
            self.article.put()
        elif is_first:
            new_first = article.version_set.ancestor(
                GLOBAL_PARENT).order('created').get()
            self.article.first_version = new_first
            self.article.put()

    def is_first(self):
        return self.key() == self.article.first_version.key()

    def is_latest(self):
        return self.key() == self.article.latest_version.key()