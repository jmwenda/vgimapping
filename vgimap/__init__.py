import os
__version__ = (0, 0, 1, 'alpha', 0)


def get_version():
    import vgimap.version
    return vgimap.version.get_version(__version__)


def main(global_settings, **settings):
    from django.core.wsgi import get_wsgi_application
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings.get('django_settings'))
    app = get_wsgi_application()
    return app
