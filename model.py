import datetime as dt
# Third party libs
from google.appengine.api.app_identity import get_application_id
from google.appengine.ext import db


SESSION_LIFETIME = 1  # day
GLOBAL_PARENT = db.Key.from_path('app', get_application_id())


class BaseModel(db.Model):
    @classmethod
    def by_prop(cls, prop_name, value, ancestor=GLOBAL_PARENT):
        q = cls.all().filter(prop_name + ' =', value).ancestor(ancestor)

        return q.get()


class User(BaseModel):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True, indexed=False)
    email = db.EmailProperty(required=False)


class Session(BaseModel):
    sid = db.StringProperty(required=True)
    user = db.ReferenceProperty(User, collection_name="Sessions")
    created = db.DateTimeProperty(auto_now_add=True)

    def has_expired(self):
        delta = dt.datetime.now() - self.created
        return delta.days > SESSION_LIFETIME


class WikiPage(BaseModel):
    url = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    body = db.TextProperty()