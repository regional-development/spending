import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta
from typing import Any, Dict, Iterator


DATE = date.today() - timedelta(days=2)
PATH = Path(__file__).resolve().parent / "data"
URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 


def to_dataframe(json_data: Dict[str, Any], page: int) -> pd.DataFrame:
    return pd.json_normalize(json_data["transactions"]).assign(page=page)


def fetch(
    session: requests.Session,
    start_date: date,
    end_date: date,
    starting_page: int = 0,
    page_size: int = 100,
) -> Iterator[pd.DataFrame]:
    params = {
        "startdate": start_date.isoformat(),
        "enddate": end_date.isoformat(),
        "page": starting_page,
        "pageSize": page_size,
    }
    next_page, last_page = starting_page, starting_page
    while next_page <= last_page:
        params["page"] = next_page
        data = session.get(URL, params=params).json()
        yield to_dataframe(data, next_page)
        next_page, last_page = next_page+1, data["count"] // data["pageSize"]
                
        
def fetch_all() -> Iterator[pd.DataFrame]:
    with requests.Session() as session:
        session.hooks["response"].append(
            lambda r, *args, **kwargs: r.raise_for_status()
        )
        yield from fetch(session, start_date=DATE, end_date=DATE)
        
        
if __name__ == "__main__":
    output_path = PATH / f"{DATE}.csv"
    output_path.unlink(missing_ok=True)
    data = fetch_all()
    for i, dataframe in enumerate(data):
        write_header = True if i == 0 else False
        dataframe.to_csv(
            output_path, header=write_header, index=False, mode="a"
        )
