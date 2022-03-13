import datetime
import logging
import pprint
from typing import List, Dict, Union, Optional
from .column import Column


class Page:
    """Page is essentially a thin wrapper of a Dict"""

    def __init__(self, data: Dict) -> None:
        self.id = data.get('id')
        self.data = data

    @property
    def is_instantiated(self) -> bool:
        # a page is instantiated if it has been pushed to the Notion servers
        # in which case the id must not be None
        return self.id is not None

    def __str__(self) -> str:
        return f"{self.id}: {pprint.pformat(self.data)}"


class PageBuilder:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.page = {}

    def build(self) -> Page:
        return Page(self.page)

    def add_column(self, col: Column, col_val: str):
        # add based on col's type
        # date/time must be added explicitly throughput add_date
        if col.type == "title":
            self.add_title(col.name, col_val)
        elif col.type == "rich_text":
            self.add_text(col.name, col_val)
        elif col.type == "multi_select":
            if col_val not in col.options:
                logging.warning(f"multi_select option not found: {col_val}")
            self.add_multi_select(col.name, col_val)
        elif col.type == "select":
            self.add_select(col.name, col_val)
            if col_val not in col.options:
                logging.warning(f"select option not found: {col_val}")
        else:
            raise ValueError("Column type not supported")

    def add_title(self, col_key: str, col_val: str):
        self.page[col_key] = {
            "type": "title",
            "title": [{
                "type": "text",
                "text": {
                    "content": col_val
                }
            }]
        }

    def add_text(self, col_key: str, col_val: str):
        if len(col_val) > 2000:
            logging.warning("Notion APIs have size limits for the content (<=2000); will truncate the text to fit the limits")
            col_val = col_val[: 2000]
        self.page[col_key] = {
            "type": "rich_text",
            "rich_text": [{
                "type": "text",
                "text": {
                    "content": col_val
                }
            }]
        }

    def add_multi_select(self, col_key: str, col_val: List[str]):
        self.page[col_key] = {
            "type": "multi_select",
            "multi_select": [{"name": v} for v in col_val]
        }

    def add_select(self, col_key: str, col_val: str):
        self.page[col_key] = {"type": "select", "select": {"name": col_val}}

    def add_date(self, col_key: str,
                 begin: Union[datetime.datetime, datetime.date],
                 end: Optional[Union[datetime.datetime, datetime.date]] = None):
        self.page[col_key] = {
            "type": "date",
            "date": {
                "start": begin.isoformat()
            }
        }
        if end is not None:
            self.page[col_key]["date"]["end"] = end.isoformat()
