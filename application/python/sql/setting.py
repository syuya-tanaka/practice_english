from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


dialect = 'postgresql'
driver = 'psycopg2'
user = 'eng_word'
password = 'eng_word'
host = 'localhost'
port = '4532'
db_name = 'eng_word'
db_url = f'{dialect}+{driver}://{user}:{password}@{host}:{port}/{db_name}'

# DB接続を管理してDBの違いを吸収するもの。
Engine = create_engine(db_url, echo=True)

# ORMを操作する際に使用するもの。
Session = sessionmaker(Engine)

# ORMを実装する際に必要なもの。これを継承してテーブルを作成する。
Base = declarative_base()
