import re
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    create_engine,
    update,
    delete,
)
from sqlalchemy.orm import declarative_base, Session


Base = declarative_base()
db_path = "jobs_creator.db"
engine = create_engine(f"sqlite:///{db_path}")


class BaseSite(Base):
    __abstract__ = True
    offer_title = Column(String)
    applicated = Column(Boolean, default=False)
    link = Column(String, unique=True)
    location = Column(String, nullable=True)
    time = Column(Date, default=date.today())
    company_name = Column(String, nullable=True)
    wages = Column(String, nullable=True)
    remote = Column(Boolean, default=False)
    id = Column(Integer, primary_key=True)
    days_until_deadline = Column(Integer, default=30)

    @classmethod
    def decrement_deadline(cls, session: Session):
        stmt = update(cls).values(days_until_deadline=cls.days_until_deadline - 1)
        session.execute(stmt)
        session.commit()

        # Deleting when offert oldest than 30 days
        delete_stmt = delete(cls).where(cls.days_until_deadline == 0)
        session.execute(delete_stmt)
        session.commit()


class NewsOffert(BaseSite):
    __tablename__ = "News_Offer"
    source = Column(String)


def date_translate(time):
    month_translations = {
        "stycznia": "January",
        "lutego": "February",
        "marca": "March",
        "kwietnia": "April",
        "maja": "May",
        "czerwca": "June",
        "lipca": "July",
        "sierpnia": "August",
        "września": "September",
        "października": "October",
        "listopada": "November",
        "grudnia": "December",
    }
    for pl_month, en_month in month_translations.items():
        time = time.replace(pl_month, en_month)

    time = datetime.strptime(time, "%d %B %Y").date()
    return time


def find_digit(text):
    pattern = r"\d+"
    digit = int(re.findall(pattern, text)[0])
    return digit


def title_checker(title):
    keywords = [
        "frontend",
        "account",
        "german",
        "french",
        "customer",
        "norwegian",
        "hr",
        "finnish",
        "arabic",
        "armenian",
        "danish",
        "kazakh",
        "romanian",
        "turkish",
        "ukrainian",
        ".net",
        "java",
        "italian",
        "dutch",
        "php",
        "helpdesk",
        "oracle",
        "manager",
        "cloud",
        "mid",
        "mid/senior",
        "senior",
        "android",
        "angular",
        "react",
        "vue.js",
        "golang",
        "support",
        "service",
        "consultant",
        "spanish",
        "projektant",
        "student",
        "administator",
        "nauczyciel",
        "instruktor",
        "trener",
        "animator",
        "elektronik",
        "technik",
        "ruby",
        "coach",
        "graduate",
        "lead",
        "unreal",
        "czech",
        "spanish",
        "slovak",
        "portuguese",
        "hydraulics",
        "art",
        "architect",
        "highway",
        "bridges",
        "greek",
        "scala",
        "dotnet",
        "virtualization",
        "ios",
        "infrastruktury",
        "robotics",
        "graphics",
        "kernel",
        "qa",
        "tester",
        "starszy",
        "scrum",
        "agile",
        "game",
        "manual",
        "linux",
        "unix",
        "c#",
        "c+" "azure",
        "e-commerce",
        "marketing",
    ]
    if any(keyword in title.lower() for keyword in keywords):
        return True
