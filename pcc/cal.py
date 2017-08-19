from datetime import timedelta

from icalendar import Calendar, Event


def make_calendar(showings) -> Calendar:
    calendar = Calendar()
    for showing in showings:
        event = Event()
        event.add('summary', showing.name)
        event.add('description', showing.description)
        event.add('dtstart', showing.start_time)
        event.add('location', 'Prince Charles Cinema')
        if showing.end_time:
            event.add('dtend', showing.end_time)
        else:
            # we don't know the end time, so say it's two hours
            event.add('dtend', showing.start_time + timedelta(hours=2))
        calendar.add_component(event)
    return calendar
