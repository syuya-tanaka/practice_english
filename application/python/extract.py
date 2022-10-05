"""A module for formatting files into pretty shapes."""
import re


class Extract_To_Translate(object):
    def __init__(self, file: str) -> None:
        self.file = file

    def remove_unneeded(self, s_line: int, e_line: int) -> str:
        """s_line行からe_line行までの間を他のファイルに書き込む。

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
        self.new_txt_file = "extracted_text.txt"
        with open(self.file, "r") as raw_file:
            for line in raw_file:
                count += 1
                if start_line <= count <= end_line:
                    extracted_data += line
            with open(self.new_txt_file, "w") as new_file:
                new_file.write(extracted_data)
        return self.new_txt_file

    def extract_eng(self, *args, **kwargs) -> list[str]:
        """translatorに渡す事ができる形に抽出する。
        """
        self.remove_unneeded(*args, **kwargs)
        with open(self.new_txt_file, "rt") as src_file:
            src_text = src_file.read()
            processed_file = re.sub("\d", "", src_text)
            processed_file = re.sub("\W", "", processed_file)
            processed_file = re.sub("[A-Z]", "", processed_file)
            result_file = re.findall("[a-z]+", processed_file)
            return result_file

# サンプルではs_line=30, e_line=949
