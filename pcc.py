import sys

from pcc.scraper import scrape_showings
from pcc.cal import make_calendar

showings = []
has_errors = False

for showing in scrape_showings():
    if showing.is_ok():
        showings.append(showing.value)
    else:
        has_errors = True
        print(showing.err(), file=sys.stderr)

calendar = make_calendar(showings)

print(calendar.to_ical().decode('utf-8'))

if has_errors:
    sys.exit(1)
