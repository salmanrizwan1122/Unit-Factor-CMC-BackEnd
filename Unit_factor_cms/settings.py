from pathlib import Path
from decouple import config  # Use the `config` function
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='your-default-secret-key')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']



# Application definition


INSTALLED_APPS = [
    "ufcmsdb",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rolesapis',
    'usersapis',
    'departmentsapis',
    'designationsapis',
    'rest_framework',
    'expenseapis',
    'projectsapi',
    'authapis',
   'attendenceapis',
    'leavesapis'
    # 'rest_framework.authtoken'

]




MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Unit_factor_cms.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': [
#         'rest_framework.authentication.TokenAuthentication',
#     ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.IsAuthenticated',
#     ],
# }
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Karachi'  # Correct time zone
USE_I18N = True
USE_TZ = True

WSGI_APPLICATION = 'Unit_factor_cms.wsgi.application'
# Database configuration
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': config('DATABASE_NAME', default='postgres'),
       'USER': config('DATABASE_USER', default='postgres'),
       'PASSWORD': config('DATABASE_PASSWORD', default=''),
       'HOST': config('DATABASE_HOST', default='127.0.0.1'),
       'PORT': config('DATABASE_PORT', default='5432'),
   }
}
# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
