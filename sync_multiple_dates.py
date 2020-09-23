import json
import requests
import pandas as pd


URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 


def fetch(session, params):
    next_page, last_page = 0, 0
    while next_page <= last_page:
        params["page"] = next_page
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
    date_range = [
        date.strftime("%Y-%m-%d") 
        for date in pd.bdate_range(start='9/1/2020', end='9/23/2020').date
    ]
    data = fetch_all(date_range)
    results = pd.DataFrame(data)
    results.to_csv(f"data/{date_range[0]}_{date_range[-1]}.csv", index=False)


if __name__ == "__main__":
    main()
