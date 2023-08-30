"""Module to test translate.py."""
import concurrent.futures
from concurrent.futures import wait
from http.client import RemoteDisconnected
import queue
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
import sys
from xmlrpc.client import ProtocolError

import pytest
import translators as ts

from apps.models import extract
from apps.models import translate


queue = queue.Queue()

TEST_ENG_LIST = ['audio', 'author', 'available', 'avoid', 'backup']
TEST_JPN_LIST = ['オーディオ', '著者', '利用可能', '避ける', 'バックアップ']


@pytest.fixture()
def my_count_list(count_list=None):
    if count_list is None:
        count_list = []
    [count_list.append(i) for i in range(5)]
    return count_list


@pytest.fixture()
def my_formatted_data():
    pdf_operator = extract.PdfOperator(extract.OUTPUT_FILE)
    return pdf_operator.exec_extract_eng(extract.START_OF_LINE,
                                         extract.END_OF_LINE)


def translate_eng_word(eng_word):
    try:
        jpn_word = ts.google(eng_word,
                             translate.FROM_LANG,
                             translate.TO_LANG)
        return jpn_word
    except (ConnectionError, RemoteDisconnected, ProtocolError):
        pass
    except HTTPError:
        print('Exceeded the daily API usage count today.')
        sys.exit(1)


class TestTranslate:
    def test_extract_eng_word(self, my_count_list, my_formatted_data):
        translator = translate.TranslateOperator(my_formatted_data,
                                                 extract.START_OF_LINE,
                                                 extract.END_OF_LINE)
        for my_count in my_count_list:
            actual = list(translator._extract_eng_word(my_count))
            assert actual[0] in TEST_ENG_LIST

    def test_run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(
                translate_eng_word,
                eng_word
            ) for eng_word in TEST_ENG_LIST]
            wait(futures)

            for future in futures:
                actual = future.result()
                assert actual in TEST_JPN_LIST

