import os
# Third-party imports
import jinja2


def timestamp_format(value, f="%d %B %Y %H:%M:%S"):
    return value.strftime(f)


jinja_environment = jinja2.Environment(
    autoescape=True, loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))
jinja_environment.lstrip_blocks = True
jinja_environment.trim_blocks = True

jinja_environment.filters['timestampformat'] = timestamp_format