import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # db
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # pagination
    PER_PAGE = 10

    # flask-whooshee
    WHOOSHEE_MIN_STRING_LEN = 1

    # label
    LABEL = ['弱习服', '中习服', '强习服']
    UP = ['否', '是']

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
