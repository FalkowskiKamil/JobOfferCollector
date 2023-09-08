from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Boolean, Date, create_engine, update
from sqlalchemy.orm import declarative_base, Session


Base = declarative_base()
db_path = "jobs_creator.db"  # Ścieżka do bazy danych
engine = create_engine(f"sqlite:///{db_path}")


class BaseSite(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    time = Column(Date, default=date.today())
    offer_title = Column(String)
    company_name = Column(String)
    location = Column(String)
    wages = Column(String, default="NaN")
    link = Column(String, unique=True)
    remote = Column(Boolean, default=False)
    applicated = Column(Boolean, default=False)
    days_until_deadline = Column(Integer, default=30)

    @classmethod
    def decrement_deadline(cls, session: Session):
        # Użyj funkcji update z SQLAlchemy do aktualizacji wartości w kolumnie
        # days_until_deadline w całej tabeli.
        stmt = update(cls).values(days_until_deadline=cls.days_until_deadline - 1)

        # Wykonaj operację aktualizacji na bazie danych za pomocą sesji.
        session.execute(stmt)
        session.commit()
        print("decrement deadline by 1 day")


class NewsOffert(BaseSite):
    __tablename__ = "News_Offer"
    source = Column(String)

def date_translate(time):
    month_translations = {
            'stycznia': 'January',
            'lutego': 'February',
            'marca': 'March',
            'kwietnia': 'April',
            'maja': 'May',
            'czerwca': 'June',
            'lipca': 'July',
            'sierpnia': 'August',
            'września': 'September',
            'października': 'October',
            'listopada': 'November',
            'grudnia': 'December'
        }
    for pl_month, en_month in month_translations.items():
        time = time.replace(pl_month, en_month)
        
    time = datetime.strptime(time, "%d %B %Y").date()
    return time