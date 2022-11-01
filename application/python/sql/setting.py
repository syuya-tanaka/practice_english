import os

from sqlalchemy import create_engine


dialect = 'postgresql'
driver = 'psycopg2'
user = 'eng_word'
password = 'eng_word'
host = 'db'
port = '4532'
db_name = 'eng_word'
db_url = f'{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'
