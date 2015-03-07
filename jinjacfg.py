import os
# Third-party imports
import jinja2


def timestamp_format(value, f="%d %B %Y, %H:%M:%S"):
    return value.strftime(f).lstrip('0')


def view_version_url(article_url, version_id):
    if article_url == '/':
        return '/_version/{}'.format(version_id)
    return '{}/_version/{}'.format(article_url, version_id)


def edit_version_url(article_url, version_id):
    if article_url == '/':
        return '/_edit/_version/{}'.format(version_id)
    return '/_edit{}/_version/{}'.format(article_url, version_id)


jinja_environment = jinja2.Environment(
    autoescape=True, loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))
jinja_environment.lstrip_blocks = True
jinja_environment.trim_blocks = True

jinja_environment.filters['timestampformat'] = timestamp_format

jinja_environment.globals['view_version_url'] = view_version_url
jinja_environment.globals['edit_version_url'] = edit_version_url
