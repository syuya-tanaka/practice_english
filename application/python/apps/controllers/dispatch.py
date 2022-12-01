"""Provision of functions that summarize each function."""
from apps.models.base import extract_queue
from apps.models.base import delete_db
from apps.models.extract import PdfOperator
from apps.models.translate import FROM_LANG
from apps.models.translate import queue
from apps.models.translate import TO_LANG
from apps.models.translate import TranslateOperator
from apps.models import word


def prepare_data():
    trans_object = TranslateOperator(PdfOperator.run(), FROM_LANG, TO_LANG)
    fully_queue = trans_object.trans_and_put_in_db_eng_to_jpn(queue)
    word.PracticeWord.all_create(fully_queue)


def redo_db():
    delete_db()
