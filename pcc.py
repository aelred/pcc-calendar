from pcc.scraper import scrape_showings
from pcc.cal import make_calendar

showings = list(scrape_showings())
calendar = make_calendar(showings)

print(calendar.to_ical().decode('utf-8'))
