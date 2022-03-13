from notion_client import Client
from typing import List, Optional

from .database import Database


class NotionService:
    def __init__(self) -> None:
        self.client = None
        self.is_auth = False
        self.db_map = None
        self.active_db = None

    def auth(self, token_path) -> None:
        with open(token_path, 'r') as f:
            token = f.read()
        self.client = Client(auth=token.strip())
        self.is_auth = True

    def search_databases(self, title: str) -> List[Database]:
        """
        Search databases matching the given title.
        This is a pure wrapper of Notion APIs with no caching.
        """
        assert self.is_auth

        cursor = None
        db_list = []
        while True:
            res = self.client.search(query=title, start_cursor=cursor,
                                     filter={'property': 'object',
                                             'value': 'database'})
            for db_data in res.get('results'):
                db_list.append(Database(self.client, db_data))
            if res['has_more']:
                cursor = res['next_cursor']
            else:
                break
        return db_list

    def fetch_databases(self) -> None:
        assert self.is_auth
        if self.db_map is not None:
            return
        self.db_map = {}
        db_list = self.search_databases(None)
        # if multiple databases have the same name, the one with the largest
        # creation timestamp will be kept
        for db in sorted(db_list, key=lambda x: x.created_time):
            self.db_map[db.name] = db

    def list_databases_name(self) -> List[str]:
        """
        List all databases available.
        If there are multiple databases with the same name, only return the one
        with the largest creation timestamp.
        """

        self.fetch_databases()
        return self.db_map.keys()

    def get_database(self, db_name: str) -> Optional[Database]:
        """
        Get the database with matched name.
        If there are multiple database with the same name, only return the one
        with the larger creation timestamp.
        """

        self.fetch_databases()
        return self.db_map.get(db_name)

    def use_database(self, db_name: str) -> None:
        self.active_db = self.get_database(db_name)
        assert self.active_db is not None
