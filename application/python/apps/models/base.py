"""A module that assists operations on tables."""
import contextlib
import datetime
import logging.config
import random

import sqlalchemy

from apps import settings
from apps.settings import Base
from apps.settings import Engine
from apps.settings import Session


logging.config.dictConfig(settings.LOGGING_CONFIG)
models_logger = logging.getLogger('models')
base_logger = logging.getLogger('base')

RECORD_COUNT = None


def init_db():
    """Initialize the database."""
    # Import 'apps.models.word' only when executing this function.
    from apps.models import word
    Base.metadata.create_all(bind=Engine)


def delete_db():
    """Drop the database."""
    # Import 'apps.models.word' only when executing this function.
    from apps.models import word
    Base.metadata.drop_all(bind=Engine)


def inspect_db():
    """Find out if there is a specific table in the database."""
    inspector = sqlalchemy.inspect(Engine)
    models_logger.debug({
        'action': 'inspect',
        'has_table': inspector.has_table('eng_words')
    })
    return inspector.has_table('eng_words')


def extract_queue(queue):
    """Get a value from a queue of arguments."""
    eng_word = queue.get()
    trans_word = queue.get()
    yield eng_word, trans_word


def get_datetime():
    """Get date."""
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_random_num(until: int, random_list=None):
    """Generate 5 numbers in the range 1 to 'until',
       Put it in a list and return it.

    Args:
        until (int): Number of records present.
        random_list (None): None.

    Returns:
        list: A list of 5 integers from 1 to 'until'.
    """
    if random_list is None:
        random_list = []
    while True:
        random_int = random.randint(1, until)
        if random_int not in random_list:
            random_list.append(random_int)
        if len(random_list) == 5:
            break
    return random_list


def fetch_record_count(practice_word):
    """Count the number of records.

    Args:
        practice_word: 'PracticeWord'.

    Returns:
        RECORD_COUNT (int): Number of records present.
    """
    global RECORD_COUNT
    if RECORD_COUNT is None:
        RECORD_COUNT = practice_word.search_count_in_db()
        base_logger.debug({
            'action': 'count record',
            'RECORD_COUNT': RECORD_COUNT,
            'status': 'success'
        })
    return RECORD_COUNT


def input_answer_num(translated):
    """Accept input from the user.

    Args:
        translated (str): A translation of the target English word
                          into Japanese.

    Returns:
        answer_num (int): User-entered digits.
    """
    try:
        answer_num = int(input(f'\nQ.「{translated}」と同じ意味のものを選べ: '))
    except ValueError:
        print('1~5の数字を入れてください')
    else:
        return answer_num


def output_question(practice_list, question_list):
    """Print out the question and return the answer.

    Args:
        practice_list : A list of instances retrieved from the DB.
        question_list : A list of English and Japanese dicts.
    """
    print('-' * 30)
    for i, question in enumerate(question_list, 1):
        for key in question:
            print(i, key)
    print('-' * 30)
    random_num = random.randint(1, 5)
    answer_obj = practice_list[random_num - 1]
    user_answer_num = input_answer_num(answer_obj.translated_parent.translated)
    if user_answer_num == random_num:
        print('正解')
        return True, answer_obj
    else:
        print('不正解')
        return False, answer_obj


def insert_answer_result_in_db(result_bool, answer_obj, practice_list):
    """Process for saving answer results in DB.

    Args:
        result_bool: User's answer result. True or False
        answer_obj: An object containing the answer to the question.
        practice_list: A list of objects pulled from the DB used in the problem.

    Returns:
        answer_obj: Enter the date of answer,
                    correct or incorrect and return to save in DB.
    """
    answer_obj = enter_value_to_order(answer_obj,
                                      'date',
                                      get_datetime())
    # Enter your answer
    answer_obj = enter_value_to_order(answer_obj,
                                      'answer',
                                      result_bool)
    base_logger.debug({
        'action': 'insert data into db',
        'result_bool': result_bool,
        'answer_obj': answer_obj,
        'date_newest': answer_obj.date_parent.newest,
        'answer_newest': answer_obj.answer_parent.newest,
        'status': 'success',
    })
    return answer_obj


def enter_value_to_order(answer_obj, parent, func):
    """The process of putting values in order and updating them.

    Args:
        answer_obj: An object containing the answer to the question.
        parent: About the parent table.
        func: A function that generates a value to put in 'answer_obj'.

    Returns:
        answer_obj: Returns 'answer_obj' with new values.
    """
    parent_obj = None

    if parent == 'date':
        parent_obj = answer_obj.date_parent
    elif parent == 'answer':
        parent_obj = answer_obj.answer_parent

    if parent_obj.newest is None:
        parent_obj.newest = func
        base_logger.debug({
            'action': 'put in data to preserve',
            'newest': parent_obj.newest,
            'status': 'success'
        })
        return answer_obj

    elif parent_obj.middle is None:
        parent_obj.middle = parent_obj.newest
        parent_obj.newest = func
        base_logger.debug({
            'action': 'put in data to preserve',
            'newest': parent_obj.newest,
            'middle': parent_obj.middle,
            'status': 'success'
        })
        return answer_obj

    elif parent_obj.oldest is None or (parent_obj.newest
                                       and parent_obj.middle
                                       and parent_obj.oldest):
        parent_obj.oldest = parent_obj.middle
        parent_obj.middle = parent_obj.newest
        parent_obj.newest = func
        base_logger.debug({
            'action': 'put in data to preserve',
            'newest': parent_obj.newest,
            'middle': parent_obj.middle,
            'oldest': parent_obj.oldest,
            'status': 'success'
        })
        return answer_obj


@contextlib.contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as exception:
        base_logger.warning(f'Occur error. {exception}')
        session.rollback()
    finally:
        session.close()

