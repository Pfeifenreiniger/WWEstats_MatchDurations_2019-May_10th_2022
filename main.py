
import requests, bs4

PROFIGHTCB_MAIN_URL = "http://www.profightdb.com/cards/wwe/monday-night-raw-"
PROFIGHTCB_URL_SUFFIX = "43395"

response = requests.get(f"{PROFIGHTCB_MAIN_URL}{PROFIGHTCB_URL_SUFFIX}.html")

webpage = response.text

soup = bs4.BeautifulSoup(webpage, "html.parser")

brand = soup.select_one("div .right-content h1").getText().strip()
card_table = soup.find(name="div", class_="table-wrapper")

card_table_rows = card_table.find_all(name="tr")
# print(card_table_rows)

matches = []

if brand.startswith("WWE Monday Night Raw") or brand.startswith("WWE Friday Night Smackdown") or brand.startswith("NXT TV"):
    for row in card_table_rows:
        match = {}
        if row.find(name="td", width="22%") != None:
            rows = row.find_all(name="td", width="22%")
            match = {
                "competitor_1" : rows[0].getText(),
                "competitor_2" : rows[1].getText()
            }
        all_tds = row.find_all(name="td")
        for td in all_tds:
            if len(td.getText()) > 1 and td.getText()[0].isdecimal():
                # print(td.getText())
                match["match_length"] = td.getText()

        if len(match) > 1:
            if match.get("match_length") == None:
                match["match_length"] = "00:00"
            matches.append(match)

    print(brand)
    print(matches)

