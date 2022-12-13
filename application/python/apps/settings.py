import os
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


dialect = 'postgresql'
driver = 'psycopg2'
user = 'eng_word'
password = 'eng_word'
host = 'localhost'
port = '4532'
db_name = 'eng_word'
db_url = f'{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'

# DB接続を管理してDBの違いを吸収するもの。
Engine = create_engine(db_url, echo=True)

# ORMを操作する際に使用するもの。
Session = sessionmaker(Engine)

# ORMを実装する際に必要なもの。これを継承してテーブルを作成する。
Base = declarative_base()

# sqlのログを保存するファイル
SQL_LOG_FILE = os.path.dirname(__file__) + '/models/byproduct/log.sql'

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(threadName)s ' +
                      'func:%(funcName)s %(message)s'
        },
    },
    'handlers': {
        'defaultHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': logging.DEBUG
        },
        'modelsHandlers': {
            'class': 'logging.FileHandler',
            'filename': SQL_LOG_FILE,
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
        'models': {
            'handlers': ['modelsHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0,
        },
        'base': {
            'handlers': ['defaultHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0
        },
        'word': {
            'handlers': ['defaultHandlers'],
            'level': logging.DEBUG,
            # 親のロガーに伝搬させない
            'propagate': 0
        },
    }
}
