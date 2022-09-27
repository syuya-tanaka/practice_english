"""A file that summarizes the log settings"""
import logging


LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(threadName)s %(message)s'
        },
    },
    'handlers': {
        'defaultHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.DEBUG
        },
        'accessDataBaseHandlers': {
            'class': 'logging.FileHandler',
            'filename': 'log.log',
            'formatter': 'standard',
            'level': logging.DEBUG,
        },
    },
    'root': {
        'handlers': ['defaultHandlers'],
        'level': logging.WARNING,
    },
    'loggers': {
        'apps': {
            'handlers': ['defaultHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0
        },
        'extract': {
            'handlers': ['defaultHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0
        },
        'access_db': {
            'handlers': ['accessDataBaseHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0,
        },
    }
}
