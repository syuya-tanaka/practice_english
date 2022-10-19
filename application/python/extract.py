"""A module for formatting files into pretty shapes."""
import re


class Extractor(object):
    def __init__(self, file: str) -> None:
        self.file = file

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
        self.new_txt_file = "extracted_text.txt"

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

    def extract_eng(self, file: str) -> list[str]:
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
