import concurrent.futures
from concurrent.futures import wait
from http.client import RemoteDisconnected
import logging.config
import queue
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from typing import Any
from typing import Generator
from xmlrpc.client import ProtocolError

import translators as ts

from apps import settings


FROM_LANG = 'en'
TO_LANG = 'ja'
DATA_TO_INJECT_DB: dict = {}

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('apps')

queue = queue.Queue()


class TranslateOperator(object):
    """pdfから抽出したデータを翻訳し、DBに注入する"""

    def __init__(self, raw_data: list, from_lang: str, to_lang: str) -> None:
        self.raw_data = raw_data
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.word_count = len(self.raw_data)
        self.thread_run_count = 0

    def _extract_eng_word(self, count: int) -> Generator:
        yield self.raw_data[count]

    def trans_eng_to_jpn(self, count: int, queue) -> None:
        self.thread_run_count += 1
        logger.debug({
            'action': 'translate',
            'raw_data': isinstance(self.raw_data, list),
            'from_lang': self.from_lang,
            'to_lang': self.to_lang,
            'count': count,
            'queue': queue,
            'status': 'run'
        })
        for eng_word in self._extract_eng_word(count):
            try:
                jpn_word = ts.google(eng_word, self.from_lang, self.to_lang)
                queue.put(eng_word)
                queue.put(jpn_word)
                self.set_eng_jpn_to_dict(eng_word, jpn_word)

            except (ConnectionError, RemoteDisconnected, ProtocolError):
                pass
            except HTTPError:
                print('Exceeded the daily API usage count today.')
                break

        logger.debug({
            'action': 'translate',
            'raw_data': isinstance(self.raw_data, list),
            'from_lang': self.from_lang,
            'to_lang': self.to_lang,
            'count': count,
            'queue': queue,
            'status': 'success'
        })

    @staticmethod
    def set_eng_jpn_to_dict(eng_word, jpn_word) -> None:
        DATA_TO_INJECT_DB[eng_word] = jpn_word

    def trans_and_put_in_db_eng_to_jpn(self, queue) -> Any:
        """英語から日本語に翻訳してDBに入れる。"""
        logger.debug({
            'data': DATA_TO_INJECT_DB,
            'length': len(DATA_TO_INJECT_DB),
            'thread_run_count': self.thread_run_count,
            'status': 'run'
        })
        print('Thread running...')
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as executor:
            futures = [executor.submit(
                self.trans_eng_to_jpn,
                word_count,
                queue
            ) for word_count in range(self.word_count)]

            print('Waiting for tasks to complete...')
            wait(futures)
            logger.debug({
                'data': DATA_TO_INJECT_DB,
                'length': len(DATA_TO_INJECT_DB),
                'thread_run_count': self.thread_run_count,
                'status': 'success'
            })
        # マルチスレッドの処理が完了してから、queueを丸々投げる。
        return queue
