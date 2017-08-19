from datetime import datetime
from icalendar import vDatetime

from nose.tools import eq_, ok_

import pcc.cal
from scraper import Showing

MOCK_SHOWING_WITH_END_TIME = \
    Showing("Up", datetime(2016, 9, 4, 20, 30), datetime(2016, 9, 4, 21, 45), "description of up")

MOCK_SHOWING = Showing("Up", datetime(2016, 9, 4, 18, 30), None, "description of up")

MOCK_SHOWINGS = [
    MOCK_SHOWING,
    MOCK_SHOWING_WITH_END_TIME,
    Showing("Up", datetime(2016, 9, 5, 18, 30), None, "different description of up"),
    Showing("Logan", datetime(2016, 9, 5, 18, 30), None, "description of logan")
]

EMPTY_CALENDAR = b"""
BEGIN:VCALENDAR
END:VCALENDAR
""".strip()


def test_can_create_a_calendar_from_a_list_of_showings():
    pcc.cal.make_calendar(MOCK_SHOWINGS)


def test_can_create_ical_representation_for_empty_list_of_showings():
    calendar = pcc.cal.make_calendar([])
    eq_(calendar.to_ical().replace(b'\r\n', b'\n').strip(), EMPTY_CALENDAR)


def test_calendar_built_from_one_showing_has_one_event():
    calendar = pcc.cal.make_calendar([MOCK_SHOWING])
    eq_(len(calendar.subcomponents), 1)


def test_calendar_built_from_one_showing_has_one_event_with_name_of_the_showing():
    calendar = pcc.cal.make_calendar([MOCK_SHOWING])
    event = calendar.subcomponents[0]
    eq_(event['summary'], MOCK_SHOWING.name)


def test_calendar_built_from_one_showing_has_one_event_with_description_of_the_showing():
    calendar = pcc.cal.make_calendar([MOCK_SHOWING])
    event = calendar.subcomponents[0]
    eq_(event['description'], MOCK_SHOWING.description)


def test_calendar_built_from_one_showing_has_one_event_with_start_time_of_the_showing():
    calendar = pcc.cal.make_calendar([MOCK_SHOWING])
    event = calendar.subcomponents[0]
    eq_(vDatetime.from_ical(event['dtstart'].to_ical()), MOCK_SHOWING.start_time)


def test_every_event_in_calendar_has_start_before_end_of_event():
    calendar = pcc.cal.make_calendar(MOCK_SHOWINGS)
    for event in calendar.subcomponents:
        ok_(event['dtstart'].to_ical() < event['dtend'].to_ical())


def test_calendar_built_from_one_showing_has_one_event_with_end_time_of_the_showing():
    calendar = pcc.cal.make_calendar([MOCK_SHOWING_WITH_END_TIME])
    event = calendar.subcomponents[0]
    eq_(vDatetime.from_ical(event['dtend'].to_ical()), MOCK_SHOWING_WITH_END_TIME.end_time)


def test_every_event_in_calendar_has_location_prince_charles_cinema():
    calendar = pcc.cal.make_calendar(MOCK_SHOWINGS)
    for event in calendar.subcomponents:
        eq_(event['location'], 'Prince Charles Cinema, 7 Leicester Pl, London WC2H 7BY, United Kingdom')

