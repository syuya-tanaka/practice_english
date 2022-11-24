"""A module for formatting files into pretty shapes."""
import logging.config
import os
import re
from typing import Any

from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

import base
from apps import settings

INPUT_FILE = '../../essential-programming-words.pdf'
OUTPUT_FILE = 'byproduct/output.txt'
START_OF_LINE = 30
END_OF_LINE = 1004

logging.config.dictConfig(settings.LOGGING_CONFIG)
logger = logging.getLogger('extract')


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


class Extractor(Explorer):
    def __init__(self, file: str) -> None:
        self.file = file
        self.new_txt_file = "byproduct/extracted_text.txt"

    def remove_unneeded(self, s_line: int, e_line: int) -> str:
        """Write lines from s_line to e_line to another file.

        Args:
            s_line (int): First line to start extracting.
            e_line (int): Last line to end extracting.

        Returns:
            str: New file completed.
        """
        start_line = s_line
        end_line = e_line
        count = 0
        extracted_data = ""

        try:
            if not type(start_line) is int or not type(end_line) is int:
                raise TypeError('入力値は共に数字である必要がある')
        except TypeError as exc:
            raise exc

        with open(self.file, "r") as raw_file:
            for line in raw_file:
                count += 1

                try:
                    if start_line >= end_line:
                        raise ValueError('start_lineはend_lineよりも小さい必要がある')
                except ValueError as exc:
                    raise exc

                if start_line <= count <= end_line:
                    extracted_data += line

            with open(self.new_txt_file, "w") as new_file:
                new_file.write(extracted_data)

        return self.new_txt_file

    @staticmethod
    def extract_eng(file: str) -> list[str]:
        """Extract into a form that can be passed to the translator."""
        with open(file, "rt") as src_file:
            src_text = src_file.read()
            processed_file = re.sub("\d", "", src_text)
            processed_file = re.sub("\W", "", processed_file)
            processed_file = re.sub("[A-Z]", "", processed_file)
            result_file = re.findall("[a-z]+", processed_file)
            return result_file

    def exec_extract_eng(self, s_line: int, e_line: int) -> list[str]:
        """Whether to process self.file or self.new_txt_file."""
        result_file = self.remove_unneeded(s_line, e_line)
        if result_file:
            return self.extract_eng(self.new_txt_file)
        else:
            raise Exception('ファイルを作成する事ができないので実行できない。')


class PdfOperator(Extractor):
    already_get_data = Explorer.is_exist_output_file()

    def __init__(self, file, judge=already_get_data) -> None:
        super().__init__(file)
        self.judge = judge

    def fetch_word(self) -> None:
        if not self.judge:
            logger.debug({
                'action': 'extract from pdf',
                'input_file': INPUT_FILE,
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
                'input_file': INPUT_FILE,
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
        pdf_operator = PdfOperator(OUTPUT_FILE)
        pdf_operator.is_exist_db()
        pdf_operator.fetch_word()
        # raw_data = Extractor(OUTPUT_FILE)
        pdf_operator.extract_place_determining()
        formatted_data = pdf_operator.exec_extract_eng(START_OF_LINE, END_OF_LINE)
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
