# -*- coding: utf-8 -*-
"""
Django settings for bibliothek project.

Generated by 'django-admin startproject' using Django 1.9.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import math
import os

from gi.repository import GLib
from . import GConfig


__author__ = 'jnphilipp'
__email__ = 'me@jnphilipp.org'
__license__ = 'GPLv3'
__version__ = '0.0.1'


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# general app info
APP_IDENTIFIER = 'bibliothek'
APP_NAME = 'bibliothek'
APP_COMMENTS = ''
APP_COPYRIGHT = 'Copyright (C) 2016 jnphilipp'
APP_WEBSITE = ''
APP_VERSION = (('#####################################################\n' +
                '#                    bibliothek                     #\n' +
                '#                                                   #\n' +
                '#%sv%s%s#\n' % (' ' * math.floor((50 - len(__version__)) / 2), __version__, ' ' * math.ceil((50 - len(__version__)) / 2)) +
                '#%s%s%s#\n' % (' ' * math.floor((51 - len(__license__)) / 2), __license__, ' ' * math.ceil((51 - len(__license__)) / 2)) +
                '#                                                   #\n'
                '#%s%s%s#\n' % (' ' * math.floor((51 - len(__author__)) / 2), __author__, ' ' * math.ceil((51 - len(__author__)) / 2)) +
                '#%s%s%s#\n' % (' ' * math.floor((51 - len(__email__)) / 2), __email__, ' ' * math.ceil((51 - len(__email__)) / 2)) +
                '#                                                   #\n' +
                '#%s%s%s#\n' % (' ' * math.floor((51 - len(APP_WEBSITE)) / 2), APP_WEBSITE, ' ' * math.ceil((51 - len(APP_WEBSITE)) / 2)) +
                '#####################################################'))
APP_LICENSE = (('This program is free software: you can redistribute it and/or modify\n'+
'it under the terms of the GNU General Public License as published by\n'+
'the Free Software Foundation, either version 3 of the License, or\n'+
'(at your option) any later version.\n'+
'\n'+
'This program is distributed in the hope that it will be useful,\n'+
'but WITHOUT ANY WARRANTY; without even the implied warranty of\n'+
'MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the\n'+
'GNU General Public License for more details.\n'+
'\n'+
'You should have received a copy of the GNU General Public License\n'+
'along with this program.  If not, see <http://www.gnu.org/licenses/>.'))
APP_AUTHORS = ['jnphilipp <me@jnphilipp.org>']
APP_DOCUMENTERS = ['jnphilipp <me@jnphilipp.org>']


# XDG config
XDG_CONFIG_DIR = GLib.get_user_config_dir()
APP_CONFIG_DIR = os.path.join(XDG_CONFIG_DIR, APP_IDENTIFIER)


# XDG cache
XDG_CACHE_DIR = GLib.get_user_cache_dir()
APP_CACHE_DIR = os.path.join(XDG_CACHE_DIR, APP_IDENTIFIER)


# XDG data
XDG_DATA_DIR = GLib.get_user_data_dir()
APP_DATA_DIR = os.path.join(XDG_DATA_DIR, APP_IDENTIFIER)


gconf = GConfig(APP_IDENTIFIER)
gconf.load()


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = gconf['SECRET_KEY']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'files',
    'journals',
    'languages',
    'links',
    'papers',
    'persons',
    'shelves',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bibliothek.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            # 'debug': config.getboolean('debug', 'TEMPLATE_DEBUG'),
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(APP_DATA_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(APP_DATA_DIR, 'static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'assets'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)


# Media files

MEDIA_ROOT = APP_DATA_DIR
