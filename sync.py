import requests
import pandas as pd
from datetime import date, timedelta


DATE = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 


def fetch(session, params):
    next_page, last_page = 0, 0
    while next_page <= last_page:
        params["page"] = next_page
        data = session.get(URL, params=params).json()
        yield pd.json_normalize(data.get("transactions"))\
                .assign(page=params.get("page"))
        next_page, last_page = next_page+1, data["count"] // data["pageSize"]
                
        
def fetch_all():
    with requests.Session() as session:
        params = {"page": 0, "pageSize": 100, "startdate": DATE, "enddate": DATE}
        yield from fetch(session, params)
        
        
if __name__ == "__main__":
    data = fetch_all()
    pd.concat(data).to_csv(f"data/{DATE}.csv", index=False)
