"""
Web-Scraping Script to collect any match-duration related data of the WWE weekly TV shows RAW, Smackdown, and NXT
from http://www.profightdb.com.
The data will cover from the year 2019 until the 10th of May 2022, to compare some time for the COVID-19 pandemic,
the pandemic itself, and a few months after WWE could have returned to live audience shows in mid 2021.
"""

import requests, bs4, calendar, sqlite3, time

##------------------------------SQLITE DATABASE CONNECTION------------------------------##
conn = sqlite3.connect('WWEmatchDuration.db')
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS MatchDurations (date TEXT, brand TEXT, wrestler_s_1 TEXT, wrestler_s_2 TEXT, match_duration_in_sec INTEGER)")

##------------------------------WEBSITE CONNECTION------------------------------##
PROFIGHTCB_MAIN_URL = "http://www.profightdb.com/cards/wwe/monday-night-raw-"
PROFIGHTCB_URL_SUFFIX = 43402 # 43402 -> NXT from 10th of May 2022
while PROFIGHTCB_URL_SUFFIX > 28675:

    response = requests.get(f"{PROFIGHTCB_MAIN_URL}{str(PROFIGHTCB_URL_SUFFIX)}.html")
    webpage = response.text

    ##------------------------------BEAUTIFUL SOUP------------------------------##
    soup = bs4.BeautifulSoup(webpage, "html.parser")
    xa=u'\xa0'

    brand = soup.select_one("div .right-content h1").getText().strip()
    raw_date = soup.select_one("div .right-content table td").getText()
    date = raw_date[raw_date.find(",")+2:]
    date = date.split()
    year = date[2]
    month = f"{int(list(calendar.month_abbr).index(date[0])):02d}"
    day = f"{int(date[1][:-2]):02d}"
    date = f"{year}-{month}-{day}"

    card_table = soup.find(name="div", class_="table-wrapper")

    card_table_rows = card_table.find_all(name="tr")

    if ("Monday Night Raw" in brand or "Smackdown" in brand or "NXT TV" in brand) and int(year) >= 2019:

        if "Raw" in brand:
            brand = "RAW"
        elif "Smackdown" in brand:
            brand = "Smackdown"
        elif "NXT" in brand:
            brand = "NXT"

        for row in card_table_rows:
            match = {}
            if row.find(name="td", width="22%") != None:
                rows = row.find_all(name="td", width="22%")
                wrestler_s_1 = rows[0].getText()
                wrestler_s_2 = rows[1].getText()
                if xa in wrestler_s_1:
                    wrestler_s_1 = wrestler_s_1.replace('\xa0', '')
                    if '(c)' in wrestler_s_1:
                        wrestler_s_1 = wrestler_s_1.replace('(c)', '')
                if "'" in wrestler_s_1:
                    wrestler_s_1 = wrestler_s_1.replace("'", '')
                if xa in wrestler_s_2:
                    wrestler_s_2 = wrestler_s_2.replace('\xa0', '')
                if "'" in wrestler_s_2:
                    wrestler_s_2 = wrestler_s_2.replace("'", '')
                match = {
                    "date" : date,
                    "brand" : brand,
                    "wrestler(s)_1" : wrestler_s_1,
                    "wrestler(s)_2" : wrestler_s_2
                }
            all_tds = row.find_all(name="td")
            for td in all_tds:
                if len(td.getText()) > 1 and ":" in td.getText() and td.getText()[:1].isdecimal():
                    # print(td.getText())
                    match_duration = td.getText()
                    match_duration_in_sec = (int(match_duration[:2]) * 60) + int(match_duration[3:])
                    match["match_duration_in_sec"] = match_duration_in_sec

            if len(match) > 1:
                if match.get("match_duration_in_sec") == None:
                    match["match_duration_in_sec"] = "0"

                sql = f"INSERT INTO MatchDurations VALUES ('{str(match['date'])}', '{str(match['brand'])}', '{str(match['wrestler(s)_1'])}', '{str(match['wrestler(s)_2'])}', '{str(match['match_duration_in_sec'])}')"
                c.execute(sql)
                conn.commit()
                print(f"A {match['brand']} match from {date} has been added to the DB.")
                time.sleep(0.5)

    PROFIGHTCB_URL_SUFFIX -= 1
    print(PROFIGHTCB_URL_SUFFIX)
    time.sleep(1)


