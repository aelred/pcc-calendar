import itertools
from datetime import datetime
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup, SoupStrainer
from dateutil.parser import parse


class Showing:
    def __init__(self, name: str, start_time: datetime, end_time: Optional[datetime], description: str):
        self.name = name
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

    def __repr__(self):
        return f'Showing({self.name}, {self.start_time}, {self.end_time}, {self.description})'


def scrape_showings() -> Iterable[Showing]:
    response = requests.get('https://princecharlescinema.com/PrinceCharlesCinema.dll/WhatsOn')
    return parse_showings(response.content)


def parse_showings(html: str) -> Iterable[Showing]:
    tree = BeautifulSoup(html, 'html.parser')
    films = tree.find_all(class_='film')
    return itertools.chain.from_iterable(_get_showings_for_film(film) for film in films)


def _get_showings_for_film(film: BeautifulSoup) -> Iterable[Showing]:
    title_elem = film.find_next(class_='seasonEventTitle')
    name = title_elem.text.strip()

    description_elem = title_elem.parent
    description = '\n'.join(p.text.strip() for p in description_elem.find_all('p')).strip()
    if description == '':
        # if there are no paragraph tags, retrieve all text, but remove the name of the movie
        description = description_elem.text.strip()[len(name):].strip()

    times = film.find_all(class_='eventPerformance')
    return (_get_showing_for_time(name, description, time_elem) for time_elem in times)


_DATE_FORMAT: str = '%a %d %b %Y'


def _get_showing_for_time(name: str, description: str, time_elem: BeautifulSoup) -> Showing:
    date_elem = time_elem.find_previous_sibling(class_='eventPerformanceDate')
    date_str = date_elem.text.strip()

    date = parse(date_str)

    time_str = time_elem.find_all('a')[1].text.strip()

    if '-' in time_str:
        # assume this includes an end time
        (start_time_str, end_time_str) = time_str.split('-')
        start_time = parse(start_time_str, default=date)
        end_time = parse(end_time_str, default=date)
    else:
        start_time = parse(time_str, default=date)
        end_time = None

    return Showing(name, start_time, end_time, description)
