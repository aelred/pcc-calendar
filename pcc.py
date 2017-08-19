from pcc.scraper import scrape_showings
from pcc.cal import make_calendar

showings = list(scrape_showings())
calendar = make_calendar(showings)

with open('pcc-calendar.ics', 'wb') as f:
    f.write(calendar.to_ical())
