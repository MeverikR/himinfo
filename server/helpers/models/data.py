import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text, select, func, and_, desc, asc, insert,update
Base = declarative_base()


__all__ = ('Data', )

class Data (Base):
    """
    Класс для таблицы data
    """
    __tablename__ = 'table'

    id = sa.Column(sa.Integer, primary_key=True)
    date_pay = sa.Column(sa.TIMESTAMP)
    contr_id = sa.Column(sa.String(250))
    debet = sa.Column(sa.String(250))
    fone_cell = sa.Column(sa.String(250))
    comment = sa.Column(sa.String())



    @classmethod
    def get_insert(self,some):
        """
        Записываем в бд результат data api
        :return:
        """
        return self.__table__.insert().values(**some)


    @classmethod
    def check_phone(self, phone):
        """
        Получить токены и сессию
        :return:
        """
        return select('*').where(self.fone_cell == phone).limit(1)

    @classmethod
    def get_select(self):
        """
        Выгружаем все поля из agbis_data
        :return:
        """
        return select([self.fone_cell,self.date_pay,self.debet,self.comment ])

    @classmethod
    def update(self,some,phone):
        """
        обновлаяем, если сумма и номер есть в бд
        :param some:
        :return:
        """
        return self.__table__.update().values(**some).where(self.fone_cell == phone)