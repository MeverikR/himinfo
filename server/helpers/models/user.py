import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, select, func, and_, desc, asc
Base = declarative_base()


__all__ = ('User', )

class User (Base):
    """
    Класс для таблицы user
    """
    __tablename__ = 'table'
    id = sa.Column(sa.Integer, primary_key=True)
    session_id = sa.Column(sa.String())
    refresh_id = sa.Column(sa.String())
    user_id = sa.Column(sa.String())
    date = sa.Column(sa.String())
    token = sa.Column(sa.String())

    @classmethod
    def get_tokens(self):
        """
        Получить токены и сессию
        :return:
        """
        return select([self.token])