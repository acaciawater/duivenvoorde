'''
Created on Sep 1, 2019

@author: theo
'''

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p%-1k1zv!b%+yk+p64q+t%dhsw**l%8!ls&-3ba6zaq_1#-4cn'

GOOGLE_MAPS_API_KEY = 'AIzaSyBZoEnkbR2kagMCHyT-CiuBzJOW3bkexBA'
GOOGLE_MAPS_API_KEY2 = 'AIzaSyBKdOTL6aLzQczCOD5EcID3IZOl1usroNI'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': 'duivenvoorde',                      # Or path to database file if using sqlite3.
        'USER': 'acacia',                      # Not used with sqlite3.
        'PASSWORD': 'Beaumont1',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
CORS_ORIGIN_ALLOW_ALL=True

DEFAULT_FROM_EMAIL = 'noreply@duivenvoorde.acaciadata.com'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER='tkleinen@gmail.com'
EMAIL_HOST_PASSWORD='Doppio66'
EMAIL_USE_TLS = True
