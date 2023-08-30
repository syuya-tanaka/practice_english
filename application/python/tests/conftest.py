"""pytest fixtures."""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        '--input_extract_range',
        action='store',
        choices=('y', 'yes', 'n', 'no'),
        default='y'
    )


@pytest.fixture
def input_extract_range(request):
    return request.config.getoption('input_extract_range')

