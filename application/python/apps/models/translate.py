import concurrent.futures
from concurrent.futures import wait
from http.client import RemoteDisconnected
import logging.config
import os
import queue
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from typing import Any
from typing import Generator
from xmlrpc.client import ProtocolError

import translators as ts
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

import base
import extract
from apps import settings

INPUT_FILE = '../../essential-programming-words.pdf'
OUTPUT_FILE = 'byproduct/output.txt'
START_OF_LINE = 30
END_OF_LINE = 1004
FROM_LANG = 'en'
TO_LANG = 'ja'
DATA_TO_INJECT_DB: dict = {}

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('apps')


class Explorer(object):
    """DBにデータを入れるかを判断するクラス。"""

    @staticmethod
    def is_exist_output_file() -> bool | None:  # type:ignore
        """output.txtの有無を確認する。

        Returns:
            int: 1
            None: None
        """
        global OUTPUT_FILE
        logger.debug({
            'action': 'find output.txt',
            'output_file': os.path.exists(OUTPUT_FILE),
            'status': 'run'
        })
        if not os.path.exists(OUTPUT_FILE):
            return False
        logger.debug({
            'action': 'find output.txt',
            'output_file': os.path.exists(OUTPUT_FILE),
            'status': 'success'
        })

    @staticmethod
    def is_exist_db() -> None:
        """dbの有無(テーブル)を確認し、存在しなければ作成する。"""
        if not base.inspect_db():
            logger.debug({
                'action': 'create db',
                'is_exist_db': base.inspect_db(),
                'status': 'run'
            })
            base.init_db()
            logger.debug({
                'action': 'create db',
                'is_exist_db': base.inspect_db(),
                'status': 'success'
            })


class PdfOperator(Explorer):
    already_get_data = Explorer.is_exist_output_file()
    input_file = INPUT_FILE

    def __init__(self, file=input_file, judge=already_get_data) -> None:
        self.file = file
        self.judge = judge
        self.output = OUTPUT_FILE

    def fetch_word(self) -> None:
        if not self.judge:
            logger.debug({
                'action': 'extract from pdf',
                'input_file': PdfOperator.input_file,
                'judge': self.judge,
                'output_file': os.path.exists(OUTPUT_FILE),
                'status': 'run'
            })
            with open(OUTPUT_FILE, 'wt') as output_file:
                laparams = LAParams(char_margin=2, line_margin=5)
                converted_pdf = extract_text(INPUT_FILE, laparams=laparams)
                output_file.write(converted_pdf)

            logger.debug({
                'action': 'extract from pdf',
                'input_file': PdfOperator.input_file,
                'judge': self.judge,
                'output_file': os.path.exists(OUTPUT_FILE),
                'status': 'success'
            })

    @staticmethod
    def input_value_decision(value: str, decision_list: list) -> bool | None:
        """Determine the input value and pass processing to each."""
        lower_value = value.lower()
        if lower_value in decision_list:
            return True
        return None

    @staticmethod
    def extract_place_determining() -> None:
        """This is where you decide where to finally pull out."""
        global START_OF_LINE
        global END_OF_LINE

        is_list_yes = ['y', 'yes']
        is_list_no = ['n', 'no']

        # is_defaultに"y"もしくは"Y"、"yes"、"Yes"等が入力された場合、デフォルト値を使用する。
        is_default = input('output.txt内のどこからどこまでを抽出したいか入力してください\n'
                           'デフォルトを使用しますか? y/n: ')
        logger.debug({
            'action': 'input of extraction point',
            'is_default': is_default,
            'start_of_line': START_OF_LINE,
            'end_of_line': END_OF_LINE,
            'status': 'run'
        })
        # デフォルトを使用する場合の処理。
        if PdfOperator.input_value_decision(is_default, is_list_yes):
            print(f'開始行: {START_OF_LINE}\n終了行: {END_OF_LINE}')

        # デフォルト値を使用せず、値を受け付ける場合の処理。
        if PdfOperator.input_value_decision(is_default, is_list_no):
            start_line = input('初めの行数を入力してください: ')
            end_line = input('終わりの行数を入力してください: ')

            try:
                START_OF_LINE = int(start_line)
                END_OF_LINE = int(end_line)
            except ValueError as err:
                print('数値のみを受け付けます。もう一度入力をしてください。\n', err)
                return PdfOperator.extract_place_determining()

        logger.debug({
            'action': 'input of extraction point',
            'is_default': is_default,
            'start_of_line': START_OF_LINE,
            'end_of_line': END_OF_LINE,
            'status': 'success'
        })

    @staticmethod
    def run() -> Any:
        global INPUT_FILE
        global OUTPUT_FILE
        global START_OF_LINE
        global END_OF_LINE
        logger.debug({
            'action': 'execute PdfOperator',
            'is_exist_db': base.inspect_db(),
            'input_file': f'{INPUT_FILE} is {os.path.exists(INPUT_FILE)}',
            'output_file': f'{OUTPUT_FILE} is {os.path.exists(OUTPUT_FILE)}',
            'start_of_line': START_OF_LINE,
            'end_of_line': END_OF_LINE,
            'status': 'run'
        })
        pdf_operator = PdfOperator()
        pdf_operator.is_exist_db()
        pdf_operator.fetch_word()
        raw_data = extract.Extractor(OUTPUT_FILE)
        pdf_operator.extract_place_determining()
        formatted_data = raw_data.exec_extract_eng(START_OF_LINE, END_OF_LINE)
        logger.debug({
            'action': 'execute PdfOperator',
            'input_file': f'{INPUT_FILE} is {os.path.exists(INPUT_FILE)}',
            'output_file': f'{OUTPUT_FILE} is {os.path.exists(OUTPUT_FILE)}',
            'start_of_line': START_OF_LINE,
            'end_of_line': END_OF_LINE,
            'formatted_data': formatted_data,
            'status': 'success'
        })
        return formatted_data


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

    def set_eng_jpn_to_dict(self, eng_word, jpn_word) -> None:
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
        with concurrent.futures.ThreadPoolExecutor(max_workers=300) as exec:
            futures = [exec.submit(
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
            # TODO マルチスレッドの処理が完了してから、queueを丸々sql.mainに投げる。


def main() -> None:
    formatted_data = PdfOperator.run()
    trans_object = TranslateOperator(formatted_data, FROM_LANG, TO_LANG)
    trans_object.trans_and_put_in_db_eng_to_jpn(queue)


if __name__ == '__main__':
    # このキューはdatabaseにデータを渡す為に存在する。
    queue = queue.Queue()
    main()
