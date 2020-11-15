import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

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
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'console'
            },
            'tiger': {
                'level': 'INFO',
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
            'level': 'INFO'
        }
    }
