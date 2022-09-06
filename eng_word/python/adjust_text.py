"""A module for formatting files into pretty shapes."""
import re


class Convert_Text_To_Save(object):
    def __init__(self, file: str) -> None:
        self.file = file
        self.result = self.string_formatting()

    def string_formatting(self) -> str:
        """Return a rough string to extract.

        Returns:
            str: The rough string.
        """
        with open(self.file, "r") as text:
            text_object = text.read()
        result = re.sub("【.*】", " ", text_object)
        result = re.sub("^/d", " ", result)
        result = re.sub("\d", "", result)
        result = re.sub("\W", "", result)
        result = re.sub("[A-Z]", "", result)
        result = result.replace("／", " ")
        result = result.replace("、", " ")
        result = result.replace("\n", "")
        return result

    def get_extracted_per_cat(self) -> tuple:
        """Return the extract for each category.

        Returns:
            str: Three things extracted for each category.
        """
        cat_list = ["ベーシック", "アドバンスト", "略語"]
        cat_addr = []
        basic_diff = 1
        adv_diff = 154
        for i in range(len(cat_list)):
            found_addr = self.result.find(cat_list[i])
            cat_addr.append(found_addr)
        self.basic_text = self.result[cat_addr[0]: cat_addr[1] - basic_diff]
        self.adv_text = self.result[cat_addr[1]: cat_addr[2] - adv_diff]
        self.acronym_text = self.result[cat_addr[2]:]
        return self.basic_text, self.adv_text, self.acronym_text

    def make_basic_list(self) -> list:
        """Create a basic list and return the sorted.

        Returns:
            list: List of sorted basic strings.
        """
        basic_eng = re.findall("[a-z]+", self.basic_text)
        basic_eng = sorted(basic_eng)
        # print(basic_eng)
        print(len(basic_eng))
        return basic_eng

    def make_advanced_list(self) -> list:
        """Create a advanced list and return the sorted

        Returns:
            list: List of sorted advanced strings.
        """
        adv_eng = re.findall("[a-z]+", self.adv_text)
        adv_eng = sorted(adv_eng)
        # print(advanced_eng)
        print(len(adv_eng))
        return adv_eng


def main() -> None:
    text = Convert_Text_To_Save("output.txt")
    text.get_extracted_per_cat()
    text.make_basic_list()
    text.make_advanced_list()


if __name__ == "__main__":
    main()
