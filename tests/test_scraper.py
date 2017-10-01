from datetime import datetime
from typing import Iterable

import httmock
from httmock import urlmatch, HTTMock
from nose.tools import eq_, ok_
from result import Result

import pcc.scraper as scraper

with open('tests/test_page.html') as f:
    mock_html = f.read()

mock_movie: str = 'MOCK MOVIE'

mock_times = {
    (datetime(2017, 9, 4, 18, 30), None),
    (datetime(2017, 9, 4, 21, 10), None),
    (datetime(2017, 9, 5, 21, 15), None),
    (datetime(2017, 9, 6, 18, 30), datetime(2017, 9, 7, 7, 30)),
    (datetime(2017, 9, 7, 21, 15), None),
    (datetime(2017, 9, 8, 21, 15), None)
}

mock_description = ' '.join("""Starting from Monday 4th September, we'll be welcoming both Tommy Wiseau &
Greg Sestero back to The Prince Charles Cinema for exclusive preview screenings of Best Friends Movie!

Cinema's most "unique" duo will be live on the PCC stage for each and every performance to answer your questions
about the film and, as always, they'll be in our bar to sign autographs & take photos [as long as you pick up a bit of
merch].

** About BEST F[R]IENDS**

When a drifter (Greg Sestero) is taken in by a peculiar mortician (Tommy Wiseau), the two hatch an underground
enterprise off the back of the mortician's old habits. But greed, hatred, and jealousy soon come in turn,
and their efforts unravel, causing the drifter to run off with the spoils and leaving the mortician adrift. An
expedition across the South West introduces wild and crazy characters through a series of twisted and dark foibles as
both men learn a valuable lesson about friendship and loyalty

https://www.bf-movie.com/ """.replace('\n\n', '\\n\\n').replace('\n', ' ').split()).strip()


# noinspection PyUnusedLocal
@urlmatch(netloc='princecharlescinema.com', path='^/PrinceCharlesCinema.dll/WhatsOn$', method='GET')
def pcc_mock(url, request):
    return httmock.response(200, mock_html)


mock_page: HTTMock = HTTMock(pcc_mock)


def test_parsing_showing_page_finds_showings_for_the_mock_movie():
    all_showings = scraper.parse_showings(mock_html)
    showings = [showing for showing in all_showings if showing.value.name == mock_movie]
    ok_(len(showings) != 0, all_showings)


def test_parsing_description_without_paragraph_tag_still_works():
    all_showings = scraper.parse_showings(mock_html)
    showing = [showing for showing in all_showings if showing.value.name == 'ANOTHER MOCK'][0]
    eq_(showing.value.description, 'Mock description of another mock without a paragraph tag')


def test_scraping_showings_from_calendar_finds_some_showings():
    with mock_page:
        all_showings = scraper.scrape_showings()
        assert len(list(all_showings)) != 0


def test_scraping_showings_from_calendar_finds_showings_for_the_mock_movie():
    with mock_page:
        all_showings = scraper.scrape_showings()
        showings = mock_movie_showings(all_showings)
        ok_(len(list(showings)) != 0, all_showings)


def test_scraping_showings_from_calendar_finds_times_for_the_mock_movie():
    with mock_page:
        all_showings = scraper.scrape_showings()
        showings = mock_movie_showings(all_showings)
        mock_movie_times = {(showing.start_time, showing.end_time) for showing in showings}
        eq_(mock_movie_times, mock_times)


def test_scraping_showings_from_calendar_finds_description_of_the_mock_movie():
    with mock_page:
        all_showings = scraper.scrape_showings()
        showings = mock_movie_showings(all_showings)
        for showing in showings:
            eq_(showing.description.replace('\n', '\\n'), mock_description)


def mock_movie_showings(showings: Iterable[Result[str, scraper.Showing]]) -> Iterable[scraper.Showing]:
    return [showing.value for showing in showings if showing.is_ok() and showing.value.name == mock_movie]
