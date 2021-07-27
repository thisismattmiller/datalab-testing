from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1wkgdvpvsoe#$mhru0i6@482_te#!6w_4+3-r8!ojkav24-w8j'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*'] 

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter',
]
COMPRESS_CSS_HASHING_METHOD = 'content'



# you can develop on dev using sqlite or postsql, just un comment the one you want to use
# if you use sqlite there are a couple things you need to comment out in base.py

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'ch_lod',
    }
}


# you will probably need to run
#  python3 manage.py migrate  
#  python3 manage.py createsuperuser
# if you switch between or create a clean slate (like delete the sqlite file)




try:
    from .local import *
except ImportError:
    pass
