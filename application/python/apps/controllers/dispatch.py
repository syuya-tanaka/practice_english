"""Provision of functions that summarize each function."""
from apps.models import base
from apps.models import extract
from apps.models import translate
from apps.models import word


def prepare_data():
    """prepare all necessary data."""
    if 30 >= word.PracticeWord.search_count_in_db():
        trans_object = translate.TranslateOperator(extract.PdfOperator.run(),
                                                   translate.FROM_LANG,
                                                   translate.TO_LANG)
        fully_queue = trans_object.run(translate.queue)
        word.PracticeWord.all_create(fully_queue)
        word.PracticeWord.ask_questions()
    else:
        word.PracticeWord.ask_questions()


def redo_db():
    """DB initialization"""
    base.delete_db()

