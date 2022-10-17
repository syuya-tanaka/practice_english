import concurrent.futures
from concurrent.futures import wait
from http.client import RemoteDisconnected
import logging
import logging.config
import os
import queue
from requests.exceptions import ConnectionError, HTTPError
from typing import Any, Generator
from xmlrpc.client import ProtocolError

import translators as ts
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

import extract
import logging_conf


INPUT_FILE = 'essential-programming-words.pdf'
OUTPUT_FILE = 'output.txt'
DATA_TO_INJECT_DB: dict = {}

logging.config.dictConfig(logging_conf.LOGGING_CONFIG)
logger = logging.getLogger('apps')


class Explorer(object):
    """DBにデータを入れるかを判断するクラス。

    Args:
        object (_type_): _description_ """

    @staticmethod
    def explore_data() -> int | None:  # type:ignore
        """output.txtの有無を確認する。

        Returns:
            int: 1
            None: None
        """
        global OUTPUT_FILE
        is_exist = os.path.exists(OUTPUT_FILE)
        if is_exist:
            return 1
        else:
            with open('output.txt', 'w'):
                OUTPUT_FILE = 'output.txt'

    @staticmethod
    # TODO マルチプロセスで作成する。実行順番優先度高め。
    def explore_db() -> None:
        """dbの有無を確認し、存在しなければ作成をする。

        Returns:
            int: 0 or 1
        """
        # if not db:
        #     access_db.
        pass

# TODO configparserを使用して、DBサーバーとの通信を可能にする。
# TODO 非同期処理の使用。


class PdfOperator(Explorer):
    already_get_data = Explorer.explore_data()
    input_file = INPUT_FILE

    def __init__(self, file=input_file, judge=already_get_data) -> None:
        self.file = file
        self.judge = judge
        self.output = OUTPUT_FILE

    def fetch_word(self) -> None:
        if not self.judge:
            # TODO DBのテーブルなり、データを入れるまでに必要な処理を裏で走らせる処理のfunc()
            logging.info({
                'action': 'extract from pdf',
                'judge': self.judge,
                'status': 'run'
            })

            with open(OUTPUT_FILE, 'wt') as output_file:
                laparams = LAParams(char_margin=2, line_margin=5)
                converted_pdf = extract_text(INPUT_FILE, laparams=laparams)
                output_file.write(converted_pdf)

            logger.info({
                'action': 'extract from pdf',
                'judge': self.judge,
                'status': 'success',
                'exist': os.path.exists(OUTPUT_FILE)
            })


class TranslateOperator(object):
    """pdfから抽出したデータを翻訳し、DBに注入する"""
    def __init__(self, raw_data: list, from_lang: str, to_lang: str) -> None:
        self.raw_data = raw_data
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.word_count = len(self.raw_data)
        self.thread_count = 0

    def _extract_eng_word(self, count: int) -> Generator:
        yield self.raw_data[count]

    def trans_eng_to_jpn(self, count: int, queue) -> None:
        self.thread_count += 1
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

    def set_eng_jpn_to_dict(self, eng_word, jpn_word) -> None:
        DATA_TO_INJECT_DB[eng_word] = jpn_word

    def trans_and_put_in_db_eng_to_jpn(self, queue) -> Any:
        """英語から日本語に翻訳してDBに入れる。"""
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
                'thread_count': self.thread_count,
                'status': 'success'
                })


def main() -> None:
    # TODO ここ内部、またはどこかで、既にデータが存在する場合の処理も書いておく
    pdf_operator = PdfOperator()
    pdf_operator.fetch_word()
    raw_data = extract.Extractor(OUTPUT_FILE)
    formatted_data = raw_data.extract_eng(30, 1004)
    trans_object = TranslateOperator(formatted_data, 'en', 'ja')
    trans_object.trans_and_put_in_db_eng_to_jpn(queue)


if __name__ == '__main__':
    # このキューはdatabaseにデータを渡す為に存在する。
    queue = queue.Queue()
    main()
