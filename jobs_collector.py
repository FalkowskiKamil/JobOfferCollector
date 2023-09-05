from solid_jobs_module import solid_jobs_function
from bulldog_module import bulldog_function
from base_module import NewsOffert
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker

from base_module import BaseSite, NewsOffert, Base, engine

solid_jobs_function()
bulldog_function()

inspector = inspect(engine)
Session = sessionmaker(bind=engine)
session = Session()
dupa = session.query(NewsOffert).filter(NewsOffert.source=="Bulldog").count()
dupa2 = session.query(NewsOffert).filter(NewsOffert.source=="Solid Jobs").count()
print(f'Bulldoga = {dupa}, solida = {dupa2}')
session.close()