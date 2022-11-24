"""A module that defines a table."""
from contextlib import contextmanager
import logging.config

from sqlalchemy import inspect

from apps import settings
from apps.settings import Base
from apps.settings import Engine
from apps.settings import Session


logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('models')


def init_db():
    from apps.models import word
    Base.metadata.create_all(bind=Engine)


def delete_db() -> None:
    from apps.models import word
    Base.metadata.drop_all(bind=Engine)


def inspect_db() -> None:
    inspector = inspect(Engine)
    logger.debug({
        'action': 'inspect',
        'has_table': inspector.has_table('eng_words')
    })
    return inspector.has_table('eng_words')


@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.warning(f'Occur error. {e}')
        session.rollback()
    finally:
        session.close()
