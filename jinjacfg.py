import os
# Third-party imports
import jinja2
# Internal project imports
from constants import error_messages


def timestamp_format(value, f="%d %B %Y, %H:%M:%S"):
    return value.strftime(f).lstrip('0')


def edit_version_url(article_url, version_id):
    if article_url == '/':
        return '/_edit/_version/{}'.format(version_id)
    return '/_edit{}/_version/{}'.format(article_url, version_id)


def delete_version_url(article_url, version_id):
    if article_url == '/':
        return '/_delete/_version/{}'.format(version_id)
    return '/_delete{}/_version/{}'.format(article_url, version_id)


def view_version_url(article_url, version_id):
    if article_url == '/':
        return '/_version/{}'.format(version_id)
    return '{}/_version/{}'.format(article_url, version_id)


def resolve_msg_from_errtype(error_type):
    return error_messages[error_type]


jinja_environment = jinja2.Environment(
    autoescape=True, loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))
jinja_environment.lstrip_blocks = True
jinja_environment.trim_blocks = True

detailed_error_messages = jinja_environment.get_template(
    'wiki/detailed_error_messages.html').module

jinja_environment.filters['timestampformat'] = timestamp_format

jinja_environment.globals.update({
    'view_version_url': view_version_url,
    'edit_version_url': edit_version_url,
    'delete_version_url': delete_version_url,
    'resolve_msg_from_errtype': resolve_msg_from_errtype,
    'getattr': getattr
})

