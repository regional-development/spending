import json
import logging
import itertools
import requests
import pandas as pd
from datetime import date, timedelta

URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 
DATE = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
START_PAGE = 0


def fetch(session, params):
    next_page, last_page = 0, 100
    while next_page <= last_page:
        params["page"] = next_page
        print(f"{params.get('startdate')=}, {next_page=}, {last_page=}")
        data = session.get(URL, params=params).json()
        yield {
            "date": params.get("startdate"), 
            "page": params.get("page"), 
            "raw_json": json.dumps(data)
        }
        next_page, last_page = next_page+1, data["count"] // data["pageSize"]
                
        
def fetch_all(date_range):
    with requests.Session() as session:
        for date in date_range:
            params = {"page": 0, "pageSize": 100, "startdate": date, "enddate": date}
            yield from fetch(session, params)
            
            
def main():
    data = fetch_all(
        ["2020-04-01", "2020-04-02", "2020-04-03", "2020-04-04"]
    )
    pd.DataFrame(data).to_csv("./data/multiple_dates.csv", index=False)