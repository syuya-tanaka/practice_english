import os

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage


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
        result = os.path.exists("./output.txt")
        print(result, "result")
        if result:
            return found
        else:
            return not_found


class Pdf_Operator(object):
    already_get_data = None
    input_file = "./essential-programming-words.pdf"

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


decision_object = Decision_To_InjectDB()
result = decision_object.explore_data()

pdf_operator = Pdf_Operator(judge=result)
pdf_operator.fetch_word()

print()