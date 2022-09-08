from functools import wraps

import os
from typing import Generator

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


class TranslateOperator(object):
    """pdfから抽出したデータを翻訳し、DBに注入する"""

    def __init__(self, phrase, from_lang, to_lang) -> None:
        self.phrase = phrase
        self.from_lang = from_lang
        self.to_lang = to_lang

    def inject_data(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print("Inject into DB from now on")
            result = func(*args, **kwargs)
            # TODO Here we will actually inject into the DB.
            print("Fully Completed")
            return result
        return wrapper

    def _extract_raw_data(self, part: int) -> Generator:
        for i in range(len(self.phrase[part])):
            yield self.phrase[part][i]

    @inject_data
    def trans_eng_to_jpn(self, part):
        for phrase in self._extract_raw_data(part):
            phrase = str(phrase)
            print(phrase)
            trans_jpn = ts.google(phrase, self.from_lang, self.to_lang)
            # 非同期処理でDBに入力をする。


def main() -> None:
    decision_object = Decision_To_InjectDB()
    result = decision_object.explore_data()

    pdf_operator = Pdf_Operator(judge=result)
    pdf_operator.fetch_word()
    phrase = adjust_text.Convert_Text_To_Save("output.txt")
    phrase.get_extract_eng()
    trans_object = TranslateOperator(phrase.extract_eng, "en", "ja")
    trans_object.trans_eng_to_jpn(0)
    # trans_object.trans_eng_to_jpn(1)


if __name__ == "__main__":
    main()
