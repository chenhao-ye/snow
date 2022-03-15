import dateutil.parser
from typing import Dict, List, Any, Optional
from notion_client.errors import APIResponseError
import pprint
import logging

from .column import Column
from .page import Page


class Database:
    def __init__(self,
                 service: 'NotionService',
                 data: Dict) -> None:
        self.service = service
        self.id = data['id']
        self.title = data['title'][0]['plain_text']
        self.created_time = dateutil.parser.isoparse(data['created_time'])
        self.data = data
        self.col_map = {k: Column(v) for k, v in data['properties'].items()}

    def __str__(self) -> str:
        return f"{self.id}: {pprint.pformat(self.data)}"

    def __getitem__(self, name: str) -> Optional[Any]:
        return self.data.get(name)

    def get_column(self, col_name: str) -> Optional[Column]:
        return self.col_map.get(col_name)

    def get_columns(self) -> List[Column]:
        return self.col_map.values()

    @property
    def name(self) -> str:
        return self.title

    def retrieve_page(self, page_id: str) -> Page:
        logging.info(f"Retrieve page {page_id}")
        return Page(self.service.pages.retrieve(page_id=page_id))

    def create_page(self, page: Page) -> Page:
        logging.info(f"Create page: {page}")
        return Page(self.service.pages.create(parent={'database_id': self.id},
                                              properties=page.data))

    def update_page(self, page_id: str, page: Page) -> Page:
        logging.info(f"Update page {page_id}: {page}")
        return Page(self.service.pages.update(page_id=page_id, properties=page.data))

    def delete_page(self, page_id: str, not_found_ok: bool = True) -> Optional[Page]:
        try:
            logging.info(f"Delete page {page_id}")
            return Page(self.service.pages.update(page_id=page_id, archived=True))
        except APIResponseError as e:
            if not_found_ok:
                logging.info(f"Delete page {page_id} response: {e}")
                return None
            # else: we are not expected to handle error here
            raise e
