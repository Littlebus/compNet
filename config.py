import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # mail
    # MAIL_SERVER = os.environ.get('MAIL_SERVER')
    # MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    # MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    # MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    # MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # pagination
    UNITS_PER_PAGE = 10
    UNITS_PER_PAGE_ADD = 3
    RECORDS_PER_PAGE = 10
    RECORDS_PER_PAGE_ADD = 3
    EVALUATIONS_PER_PAGE_ADD = 10

    # flask-msearch
    MSEARCH_INDEX_NAME = 'msearch'
    MSEARCH_BACKEND = 'whoosh'
    MSEARCH_PRIMARY_KEY = 'id'
    MSEARCH_ENABLE = False # bug in flask-msearch

    # log
    LOG_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(levelname)s %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            },
            'tiger': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'console',
                'filename': os.path.join(basedir, 'logs/care.log'),
                'maxBytes': 1024*1024*100,  # 100MB
                'backupCount': 5,
                'encoding': 'utf-8',
            }
        },
        'root': {
            'handlers': ['console', 'tiger'],
            'level': 'DEBUG'
        }
    }
