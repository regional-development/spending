import json
import random
import logging
import asyncio
import aiohttp
import pandas as pd
from datetime import datetime

URL = "https://spending.gov.ua/portal-api/v2/api/transactions/page/" 
DATE = "2020-09-16"
PAGES = 10
CONCURRENT_CONNECTIONS = 5


async def fetch(sem, session, page):
    params = {"page": page, "pageSize": 100,"startdate": DATE, "enddate": DATE}
    async with sem, session.get(URL, params=params, raise_for_status=True) as response:
        data = await response.json()
        return {"date": DATE, "page": page, "raw_json": json.dumps(data)}


async def fetch_all(loop):
    sem = asyncio.BoundedSemaphore(CONCURRENT_CONNECTIONS)
    async with aiohttp.ClientSession(loop=loop) as session:
        results = await asyncio.gather(
            *[fetch(sem, session, page) for page in range(PAGES+1)]
        )
        return pd.DataFrame(results)


def main():
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(fetch_all(loop))
    data.to_csv(f"data/sample.csv", index=False)
 

if __name__ == "__main__":
   main()