from functools import wraps
import logging
import logging.config
import os
import threading
import time
from typing import Any, Callable, Generator

import translators as ts
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import extract
import logging_conf


INPUT_FILE = 'essential-programming-words.pdf'
OUTPUT_FILE = 'output.txt'
RAW_DATA_1: dict = dict()
RAW_DATA_2: dict = dict()
DATA_TO_INJECT_DB: list = [RAW_DATA_1, RAW_DATA_2]

logging.config.dictConfig(logging_conf.LOGGING_CONFIG)
logger = logging.getLogger('apps')


class Confirm_To_Inject_To_Db(object):
    """DBにデータを入れるかを判断するクラス。

    Args:
        object (_type_): _description_ """

    @staticmethod
    def explore_data() -> int:
        """output.txtの有無を確認する。

        Returns:
            int: 0 or 1
        """
        result = os.path.exists(OUTPUT_FILE)
        if result:
            return 1
        else:
            return 0

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

# TODO Decision_To_InjectDBクラスをPdf_Operatorクラスに継承する。
# TODO configparserを使用して、DBサーバーとの通信を可能にする。
# TODO 非同期処理の使用。


class Pdf_Operator(object):
    already_get_data = Confirm_To_Inject_To_Db.explore_data()
    input_file = INPUT_FILE

    def __init__(self, file=input_file, judge=already_get_data) -> None:
        self.file = file
        self.judge = judge
        self.output = OUTPUT_FILE

    def fetch_word(self) -> None:
        if not self.judge:
            # TODO DBのテーブルなり、データを入れるまでに必要な処理を裏で走らせる処理のfunc()
            with open(self.file, 'rb') as input:
                logging.info({
                    'action': 'extract from pdf',
                    'judge': self.judge,
                    'status': 'run'
                })
                with open(self.output, 'w') as output:
                    laparams = LAParams(char_margin=20, line_margin=1)
                    resourse_manager = PDFResourceManager()
                    device = TextConverter(
                        resourse_manager, output, laparams=laparams
                    )
                    interpreter = PDFPageInterpreter(resourse_manager, device)
                    for page in PDFPage.get_pages(input):
                        interpreter.process_page(page)
                logger.info({
                    'action': 'extract from pdf',
                    'judge': self.judge,
                    'status': 'success'
                })


def inject_data(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print('Inject into DB from now on')
        result = func(self, *args, **kwargs)
        # TODO Here we will actually inject into the DB.
        print('Fully Completed')
        return result
    return wrapper


class TranslateOperator(object):
    """pdfから抽出したデータを翻訳し、DBに注入する"""

    def __init__(self, raw_data: list, from_lang: str, to_lang: str) -> None:
        self.raw_data = raw_data
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.ja_list: list = list()

    def _extract_eng_word(self, part: int, count: int) -> Generator:
        yield self.raw_data[part][count]

    def trans_eng_to_jpn(self, part: int, count: int) -> None:
        for eng_word in self._extract_eng_word(part, count):
            logger.debug({
                'action': 'translate',
                'eng_word': eng_word,
                'part': part,
                'status': 'run'
            })
            after_trans = ts.google(eng_word, self.from_lang, self.to_lang)
            DATA_TO_INJECT_DB[part][eng_word] = after_trans

    def trans_and_put_in_db_eng_to_jpn(self) -> Any:
        """英語から日本語に翻訳してDBに入れる。

        Args:
            part (int): self.raw_data[0] or self.raw_data[1] only

        Returns:
            Any: 最終的に返す値はまだ未定。多分DBからランダムに返すようにする。
        """
        # TODO part=0, part=1をマルチプロセスで処理する。
        t1 = time.time()
        for part in range(len(self.raw_data)):
            for eng_word_count in range(len(self.raw_data[part])):
                t = threading.Thread(target=self.trans_eng_to_jpn,
                                     args=(part, eng_word_count))
                t.start()
            for thread in threading.enumerate():
                if thread is threading.currentThread():
                    continue
                thread.join()
                # TODO 2 section=phraseとtrans_jpnをDBに入れる。
                # 非同期処理でDBに入力をする処理と、translate apiを使用する処理を分ける。
        logger.debug(f'DATA_TO_INJECT_DB: {DATA_TO_INJECT_DB}')
        result_time = time.time() - t1
        print(result_time)
        return self.ja_list


def main() -> None:
    # ここ内部、またはどこかで、既にデータが存在する場合の処理も書いておく
    pdf_operator = Pdf_Operator()
    pdf_operator.fetch_word()
    raw_data = extract.Convert_Text_To_Save(OUTPUT_FILE)
    formatted_data = raw_data.get_extract_eng()
    trans_object = TranslateOperator(formatted_data, 'en', 'ja')
    trans_object.trans_and_put_in_db_eng_to_jpn()


if __name__ == '__main__':
    main()
