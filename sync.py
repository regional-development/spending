import json
import logging
import itertools
import requests
import pandas as pd
from datetime import date, timedelta

URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 
DATE = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
START_PAGE = 0


def fetch(session):
    for page in itertools.count(START_PAGE):
        params = {
            "page": page, "pageSize": 100, 
            "startdate": DATE, "enddate": DATE
        }
        data = session.get(URL, params=params).json()
        logging.info(f"requests page {page}")
        if data.get("transactions"):
            yield {
                "date": DATE, 
                "page": page, 
                "raw_json": json.dumps(data)
            }
        else:
            break
        
        
def fetch_all():
    with requests.Session() as session:
        yield from fetch(session)
        
        
def main():
    data = pd.DataFrame(fetch_all())
    data.to_csv(f"data/{DATE}.csv", index=False)


if __name__ == "__main__":
    main()
    
