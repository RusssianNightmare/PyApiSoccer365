from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from db import Base, engine


# relationship!

class League(Base):
    __tablename__ = 'leagues'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    country = Column(String, nullable=False)

class Club(Base):
    __tablename__ = 'clubs'
    id = Column(Integer, primary_key=True)
    club = Column(String(32), unique=True, nullable=False, index=True)
    league = Column(ForeignKey(League.id), index=True, nullable=False)

    def __repr__(self):
        return f'{self.id} Клуб {self.club}'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    club_id = Column(Integer, ForeignKey(Club.id), nullable=False)



class Shedule(Base):
    __tablename__ = 'shedule'
    id = Column(Integer, primary_key=True)
    home_team = Column(Integer, ForeignKey(Club.id), index=True, nullable=False)
    away_team = Column(Integer, ForeignKey(Club.id), index=True, nullable=False)
    match_date = Column(DateTime, nullable=False)


if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)


# vasya       anton
# masha       masha
# petya       olya
# anton       petya
# olya        vasya