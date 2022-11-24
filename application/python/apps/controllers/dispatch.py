"""Provision of functions that summarize each function."""
from apps.models.extract import PdfOperator
from apps.models.translate import FROM_LANG
from apps.models.translate import TO_LANG
from apps.models.translate import TranslateOperator
from apps.models.translate import queue


def prepare_data():
    trans_object = TranslateOperator(PdfOperator.run(), FROM_LANG, TO_LANG)
    trans_object.trans_and_put_in_db_eng_to_jpn(queue)

