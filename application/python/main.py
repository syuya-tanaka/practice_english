""" starting point."""
from apps.controllers import dispatch


if __name__ == '__main__':
    dispatch.prepare_data()
    # If you want to initialize db
    # dispatch.redo_db()
