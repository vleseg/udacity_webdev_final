import jinja2
import os


def datetime_format(value, f="%H:%M %d.%m.%Y"):
    return value.strftime(f)


jinja_environment = jinja2.Environment(
    autoescape=True, loader=jinja2.FileSystemLoader(
        os.path.join(os.path.dirname(__file__), 'templates')))


jinja_environment.filters['datetimeformat'] = datetime_format