""" starting point."""
from apps.controllers import dispatch
from apps.models import extract


if __name__ == '__main__':
    extract.Extractor.is_exist_db()
    dispatch.prepare_data()

