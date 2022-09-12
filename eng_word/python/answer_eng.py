from functools import wraps
import os
from typing import Any, Callable, Generator

import translators as ts
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import adjust_text


class Decision_To_InjectDB(object):
    """このクラスはPdf_Operatorクラスのコンストラクタ内でjudgeを求める際に使用する。

    Args:
        object (_type_): _description_
    """

    def explore_data(self) -> int:
        """output.txtの有無と、DBに入り、データの有無を確認しにいく。

        Returns:
            int: 0 or 1
        """
        found = 1
        not_found = 0
        result = os.path.exists("output.txt")
        print(result, "result")
        if result:
            return found
        else:
            return not_found


class Pdf_Operator(object):
    already_get_data = None
    input_file = "essential-programming-words.pdf"

    def __init__(self, file=input_file, judge=already_get_data) -> None:
        self.file = file
        # TODO explore_data() return enters judge
        self.judge = judge

    def fetch_word(self) -> None:
        if not self.judge:
            # TODO DBのテーブルなり、データを入れるまでに必要な処理を裏で走らせる処理のfunc()
            with open(self.file, "rb") as input:
                with open("output.txt", "w") as output:
                    laparams = LAParams(char_margin=20, line_margin=1)
                    resourse_manager = PDFResourceManager()
                    device = TextConverter(
                        resourse_manager, output, laparams=laparams
                    )
                    interpreter = PDFPageInterpreter(resourse_manager, device)
                    for page in PDFPage.get_pages(input):
                        interpreter.process_page(page)


def inject_data(func) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print("Inject into DB from now on")
        result = func(self, *args, **kwargs)
        print(self.ja_list)
        # TODO Here we will actually inject into the DB.
        print("Fully Completed")
        return result
    return wrapper


class TranslateOperator(object):
    """pdfから抽出したデータを翻訳し、DBに注入する"""

    def __init__(self, phrase: list, from_lang: str, to_lang: str) -> None:
        self.phrase = phrase
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.ja_list: list = list()

    def _extract_raw_data(self, part: int) -> Generator:
        for i in range(len(self.phrase[part])):
            yield self.phrase[part][i]

    @inject_data
    def trans_and_put_in_db_eng_to_jpn(self, part: int) -> Any:
        """英語から日本語に翻訳してDBに入れる。

        Args:
            part (int): self.phrase[0] or self.phrase[1] only

        Returns:
            Any: 最終的に返す値はまだ未定。多分DBからランダムに返すようにする。
        """
        for phrase in self._extract_raw_data(part):
            print(phrase)
            # 1 section=抽出したphraseをgoogle-apiに投げて、self.ja_listにappend()
            trans_jpn = ts.google(phrase, self.from_lang, self.to_lang)
            self.ja_list.append(trans_jpn)
            # TODO 2 section=phraseとtrans_jpnをDBに入れる。
        return self.ja_list
        # 日本語だけをリスト化してまとめそれをリターンする。
        # 非同期処理でDBに入力をする処理と、translate apiを使用する処理を分ける。


def main() -> None:
    decision_object = Decision_To_InjectDB()
    result = decision_object.explore_data()

    pdf_operator = Pdf_Operator(judge=result)
    pdf_operator.fetch_word()
    raw_phrase = adjust_text.Convert_Text_To_Save("output.txt")
    phrase = raw_phrase.get_extract_eng()
    trans_object = TranslateOperator(phrase, "en", "ja")
    trans_object.trans_and_put_in_db_eng_to_jpn(part=0)
    # trans_object.trans_eng_to_jpn(1)


if __name__ == "__main__":
    main()
