"""Module to test extract.py."""
import os.path
import re

import pytest

from apps.models import base
from apps.models import extract


INPUT_FILE = 'essential-programming-words.pdf'
OUTPUT_FILE = 'apps/models/byproduct/output.txt'
NEW_TEXT_FILE = 'apps/models/byproduct/extracted_text.txt'
START_OF_LINE = 30
END_OF_LINE = 1004


class TestExplorer(object):
    def test_is_exist_out_put_file(self):
        """Returns None if the file exists, False otherwise."""
        result = extract.Explorer().is_exist_output_file()
        assert result is None

    def test_is_exist_db(self):
        """Check if the DB has been created."""
        extract.Explorer().is_exist_db()
        result = base.inspect_db()
        assert result is True


class TestExtractor:
    def test_remove_unneeded(self):
        extractor = extract.Extractor(OUTPUT_FILE)
        created_file = extractor.remove_unneeded(START_OF_LINE,
                                                 END_OF_LINE)
        assert os.path.exists(created_file) is True

    @pytest.mark.parametrize(
        's_line, e_line, expectation',
        [
            ('asdf', 33, pytest.raises(TypeError)),
            (33, '2342', pytest.raises(TypeError)),
            (500, 39, pytest.raises(ValueError))
        ]
    )
    def test_remove_unneeded_param(self, s_line, e_line, expectation):
        extractor = extract.Extractor(OUTPUT_FILE)
        with expectation:
            extractor.remove_unneeded(s_line, e_line)

    @staticmethod
    def test_extract_eng():
        actual = extract.Extractor.extract_eng(NEW_TEXT_FILE)
        actual = ', '.join(actual)
        re.search('[\u3041-\u309F]+', actual)

    @pytest.mark.parametrize(
        's_line, e_line, expectation',
        [
            ('asdf', 33, pytest.raises(Exception)),
            (33, '2342', pytest.raises(Exception)),
            (500, 39, pytest.raises(Exception))
        ]
    )
    def test_exec_extract_eng(self, s_line, e_line, expectation):
        extractor = extract.Extractor(OUTPUT_FILE)
        with expectation:
            extractor.exec_extract_eng(s_line, e_line)


class TestPdfOperator:
    already_get_data = extract.Explorer.is_exist_output_file()
    operator = extract.PdfOperator(OUTPUT_FILE)

    def test_fetch_word(self):
        TestPdfOperator.operator.fetch_word()
        assert os.path.exists(OUTPUT_FILE) is True

    @pytest.mark.parametrize(
        'value, decision_list, expectation',
        [
            ('y', ['y', 'yes'], True),
            ('n', ['n', 'no'], True),
            ('n', ['y', 'yes'], None),
            ('y', ['n', 'no'], None),
        ]
    )
    def test_input_value_decision_param(self,
                                        value: str,
                                        decision_list: list,
                                        expectation: bool):
        actual = TestPdfOperator.operator.input_value_decision(value,
                                                               decision_list)
        assert actual is expectation

    def test_extract_place_determining(self, input_extract_range):
        if input_extract_range == 'y' or 'yes':
            actual = extract.PdfOperator.input_value_decision(
                input_extract_range,
                ['y', 'yes']
            )
            assert actual is True
        else:
            actual = extract.PdfOperator.input_value_decision(
                input_extract_range,
                ['y', 'yes']
            )
            assert actual is None
