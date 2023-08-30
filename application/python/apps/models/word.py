"""A module that defines a table."""
import logging.config

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import UniqueConstraint

from apps import settings
from apps.settings import Base
from apps.models import base


logging.config.dictConfig(settings.LOGGING_CONFIG)
models_logger = logging.getLogger('models')
word_logger = logging.getLogger('word')

# queueに入っていた個数
QUEUE_COUNT = None

# DBに入っているレコード数
RECORD_COUNT = None


class EngWord(Base):
    """A table containing eng_words"""

    __tablename__ = "eng_words"
    __table_args__ = (UniqueConstraint("id", name="unique_eng"),)

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    eng_word = Column(Text)

    # 関連付け(親テーブル)
    eng_child = relationship(
        "PracticeWord", back_populates="eng_parent", uselist=False
    )

    def __init__(self, eng_word: str):
        self.eng_word = eng_word


class Translated(Base):
    """A table containing translated."""

    __tablename__ = "translateds"
    __table_args__ = (UniqueConstraint("id", name="unique_trans"),)

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    translated = Column(Text)

    # 関連付け(親テーブル)
    translated_child = relationship(
        "PracticeWord", back_populates="translated_parent", uselist=False
    )

    def __init__(self, translated: str):
        self.translated = translated


class Answer(Base):
    """A table of answers."""

    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("id", name="unique_answer"),)

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    newest = Column(Boolean, nullable=True)
    middle = Column(Boolean, nullable=True)
    oldest = Column(Boolean, nullable=True)

    # 関連付け(親テーブル)
    answer_child = relationship(
        "PracticeWord", back_populates="answer_parent", uselist=False
    )

    def __init__(self, answer: str = None):
        self.answer = answer


class AnswerDate(Base):
    """A table of the dates of the answers."""

    __tablename__ = "answer_dates"
    __table_args__ = (UniqueConstraint("id", name="unique_date"),)

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    newest = Column(DateTime, nullable=True)
    middle = Column(DateTime, nullable=True)
    oldest = Column(DateTime, nullable=True)

    # 関連付け(親テーブル)
    date_child = relationship(
        "PracticeWord", back_populates="date_parent", uselist=False
    )

    def __init__(self, answer_date: str = None):
        self.answer_date = answer_date


class PracticeWord(Base):
    """Table of PracticeWords."""

    __tablename__ = "practice_words"
    __table_args__ = (UniqueConstraint("id", name="unique_practice"),)

    id = Column(Integer, nullable=False, autoincrement=True, primary_key=True)
    eng_id = Column(
        ForeignKey("eng_words.id", ondelete="CASCADE"),
        name="foreignkey_eng",
        nullable=False,
    )
    trans_id = Column(
        ForeignKey("translateds.id", ondelete="CASCADE"),
        name="foreignkey_trans",
        nullable=False,
    )
    answer_id = Column(
        ForeignKey("answers.id", ondelete="CASCADE"),
        name="foreignkey_answer",
        nullable=True,
    )
    answer_date_id = Column(
        ForeignKey("answer_dates.id", ondelete="CASCADE"),
        name="foreignkey_date",
        nullable=True,
    )

    # 関連付け(子テーブル)
    eng_parent = relationship("EngWord", back_populates="eng_child")

    # 関連付け(子テーブル)
    translated_parent = relationship(
        "Translated", back_populates="translated_child"
    )

    # 関連付け(子テーブル)
    answer_parent = relationship("Answer", back_populates="answer_child")

    # 関連付け(子テーブル)
    date_parent = relationship("AnswerDate", back_populates="date_child")

    def __init__(self, eng, trans, answer=None, date=None):
        self.eng_parent = EngWord(eng)
        self.translated_parent = Translated(trans)
        self.answer_parent = Answer(answer)
        self.date_parent = AnswerDate(date)

    @classmethod
    def create(cls, eng, trans, answer=None, date=None):
        practice_word = PracticeWord(eng, trans, answer, date)
        with base.session_scope() as session:
            session.add(practice_word)

    @classmethod
    def all_create(cls, queue):
        # ここにキューから値を取り出して、それら全てをDBに入れる処理を書く。
        global QUEUE_COUNT
        QUEUE_COUNT = (queue.qsize() / 2)

        count = (queue.qsize() / 2)
        while True:
            count -= 1
            with base.session_scope() as session:
                for eng, trans in base.extract_queue(queue):
                    practice_word = PracticeWord(eng, trans)
                    session.add(practice_word)
            if not count:
                break

    @classmethod
    def search_count_in_db(cls):
        with base.session_scope() as session:
            result = session.query(PracticeWord).count()
            return result

    @classmethod
    def ask_questions(cls, practice_list=None, question_list=None):
        try_count = int(input('何回挑戦しますか: '))
        recode_count = base.fetch_record_count(cls)
        while True:
            try_count -= 1
            if try_count < 0:
                break
            if practice_list is None and question_list is None:
                practice_list = []
                question_list = []

            with base.session_scope() as session:
                for random_i in base.create_random_num(recode_count):
                    practice = session.query(cls).get(random_i)
                    practice_list.append(practice)
                    if len(practice_list) == 5:
                        for practice_obj in practice_list:
                            eng_word = practice_obj.eng_parent.eng_word
                            translated = practice_obj.translated_parent.translated
                            question_list.append({
                                eng_word: translated
                            })

                        result_bool, answer_obj = base.output_question(practice_list,
                                                                       question_list)
                        # Put value in DB based on 'result_bool'.
                        base.insert_answer_result_in_db(result_bool,
                                                        answer_obj,
                                                        practice_list)
                        word_logger.debug({
                            'action': 'save input from user',
                            'eng_word': answer_obj.eng_parent.eng_word,
                            'answer_date': answer_obj.date_parent.newest,
                            'answer_parent': answer_obj.answer_parent.newest,
                            'status': 'success'
                        })
                        print('\n')
                        practice_list, question_list = None, None
                        break

