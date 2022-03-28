import json
import os

from typing import Optional

import parsel
import requests

from loguru import logger

OUTPUT_PATH = os.path.dirname(os.path.abspath(__file__)) + \
    "/raw_data/review_ids_and_links.jl"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36"
    )
}


URL = (
    "https://www.winemag.com/?s=&drink_type=wine&page={page}&"
    "sort_by=pub_date_web&sort_dir=desc&search_type=reviews"
)

class Producer(object):
    def __new__(cls):
        pass


class SearchRetriever:
    def __init__(self, page: int) -> None:
        self.page = page
        self.url = URL.format(page=page)

    def request(self) -> Optional[requests.Response]:
        try:
            response = requests.get(self.url, headers=HEADERS)
        except Exception as e:
            logger.error(f"Request to {self.url} failed")
            logger.error(e)
        
        if response.status_code == 200:
            return response
        
        return None

    def parse_response(self) -> None:
        response = self.request()

        if not response:
            return

        selector = parsel.Selector(response.text)
        review_items = (
            selector
            .xpath("//li[@class='review-item ']")
            .xpath("./a[contains(@class, 'review-listing')]")
        )
        
        links = review_items.xpath("@href").getall()
        ids = review_items.xpath("@data-review-id").getall()

        with open(OUTPUT_PATH, 'a') as f:
            for _id, link in zip(ids, links):
                print(json.dumps({'link': link, 'id': int(_id)}), file=f)
