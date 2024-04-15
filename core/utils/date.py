from datetime import date
from typing import Generator, Tuple

def current_year():

    return date.today().year

def is_current_year(ano:int)->bool:

    return ano == current_year()

def current_month():

    return date.today().month
