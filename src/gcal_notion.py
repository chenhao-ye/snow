import os
import sys
import shutil
import argparse
import datetime
import pprint
import logging
import hashlib
from collections import OrderedDict
from typing import Dict, List, Tuple
from service.gcal import GoogleCalendarService
from service.gcal.calendar import Calendar
from service.notion import NotionService
from service.notion.database import Column, Database
from service.notion.page import PageBuilder
from local.config import Config
from local.data import DurableMap

DATA_DIR = os.path.join(os.environ['SNOW_HOME'], 'data', 'gcal_notion')
CACHED_CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
CACHED_GCAL_CREDS_PATH = os.path.join(DATA_DIR, 'gcal_creds.json')
CACHED_GCAL_TOKEN_PATH = os.path.join(DATA_DIR, 'gcal_token.json')
CACHED_NOTION_TOKEN_PATH = os.path.join(DATA_DIR, 'notion_token.json')

DURABLE_MAP_PATH = os.path.join(DATA_DIR, 'gcal_notion.db')

gcal = GoogleCalendarService()
notion = NotionService()


def get_gcal_cal_name_list() -> List[str]:
    if not gcal.is_auth:
        gcal.auth(config.get_parsed_val('gcal_creds_path'),
                  config.get_parsed_val('gcal_token_path'))
    return gcal.list_calendars_name()


def get_notion_db_name_list() -> List[str]:
    if not notion.is_auth:
        notion.auth(config.get_parsed_val('notion_token_path'))
    return notion.list_databases_name()


def get_notion_active_db() -> Database:
    if not notion.is_auth:
        notion.auth(config.get_parsed_val('notion_token_path'))
    if notion.active_db is None:
        # force config to set active db through parser `set_active_db`
        config.get_parsed_val("db_name")
    return notion.active_db


def get_notion_db_col_list() -> List[Column]:
    return get_notion_active_db().get_columns()


def check_file_exist(file_path: str) -> str:
    if not os.path.isfile(file_path):
        raise ValueError(f"File {file_path} not found")
    return file_path


def parse_cal_list(cal_list_str: str) -> List[Calendar]:
    valid_cal_name_list = get_gcal_cal_name_list()
    cal_list = []
    for cal_name in cal_list_str.split(','):
        cal_name = cal_name.strip()
        if cal_name not in valid_cal_name_list:
            raise ValueError(f"Calendar {cal_name} not found")
        else:
            cal_list.append(gcal.get_calendar(cal_name))
    return cal_list


def set_active_db(db_name: str) -> None:
    if db_name not in get_notion_db_name_list():
        raise ValueError(f"Database {db_name} not found")
    notion.use_database(db_name)


def parse_datetime(datetime_str: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(datetime_str).astimezone()


def parse_field_col_map(map_str: str) -> Dict[str, Column]:
    valid_field_list = GoogleCalendarService.FIELDS
    db = get_notion_active_db()
    field_col_map = OrderedDict()
    for m in map_str.split(','):
        field, col_name = m.split(':', 1)
        if field not in valid_field_list:
            raise ValueError(f"Calendar field {field} not found")
        col = db.get_column(col_name)
        if col is None:
            raise ValueError(f"Database column {col_name} not found")
        field_col_map[field] = col
    return field_col_map


def parse_cal_merge(merge_str: str) -> Dict[str, str]:
    cal_merge_map = OrderedDict()
    if merge_str is None:  # it is okay to have no calendar merge
        return cal_merge_map
    for m in merge_str.split(','):
        cal_src, cal_dst = m.split('>', 1)
        cal_merge_map[cal_src] = cal_dst
    return cal_merge_map


def parse_col_const(col_str) -> List[Tuple[Column, str]]:
    db = get_notion_active_db()
    # this is not implemented as a Dict but a List, because there is no
    # key-value lookup operation
    col_const_list = []
    for c in col_str.split(','):
        col_name, const = c.split('=', 1)
        col = db.get_column(col_name)
        if col is None:
            raise ValueError(f"Database column {col_name} not found")
        col_const_list.append((col, const))
    return col_const_list


def get_config() -> Config:
    config = Config()
    config.add("gcal_creds_path",
               "Path to the Google credentials JSON file",
               default=CACHED_GCAL_CREDS_PATH,
               parser=check_file_exist)
    config.add(
        "gcal_token_path",
        "Path to the Google Calendar token JSON file",
        default=CACHED_GCAL_TOKEN_PATH,
        hinter=lambda:
        f"Default use cached one; if no cache found and no token file provided, will prompt for authentication"
    )
    config.add("notion_token_path",
               "Path to the Notion token JSON file",
               default=CACHED_NOTION_TOKEN_PATH,
               parser=check_file_exist)
    config.add(
        "cal_list",
        "Calendar(s) to synchronize [cal1,cal2,...]",
        hinter=lambda: f"Valid calendars: {list(get_gcal_cal_name_list())}",
        parser=parse_cal_list)
    config.add(
        "db_name",
        "Database to which calendars are synchronized",
        hinter=lambda: f"Valid databases: {list(get_notion_db_name_list())}",
        parser=set_active_db)
    config.add("time_min",
               "Date from which start synchronize: [YYYY-MM-DD]",
               default=datetime.date.today().isoformat(),
               parser=parse_datetime)
    config.add(
        "field_col_map",
        "Customize Google Calendar Event fields to Notion Database Column [field1:col1,field2:col2,...]",
        hinter=lambda:
        f"Valid Google Calendar fields: {GoogleCalendarService.FIELDS}\n"
        f"Valid Notion Database columns: {list(str(c) for c in get_notion_db_col_list())}",
        parser=parse_field_col_map)
    config.add(
        "col_const",
        "Customize synchronized Notion Database Columns to some constant [col1=const1,col2=const2,...]",
        hinter=lambda:
        f"Valid Notion Database columns: {list(str(c) for c in get_notion_db_col_list())}",
        default=None,
        parser=parse_col_const)
    config.add(
        "cal_merge",
        "Customize to merge one calendars into another on Notion [cal1>cal2,cal3>cal4,...]",
        default=None,
        parser=parse_cal_merge)
    return config


config = get_config()


def load_config() -> None:
    arg_parser = argparse.ArgumentParser(
        prog="snow gcal-notion",
        description='Synchronize Google Calendar to Notion.')

    if os.path.isfile(CACHED_CONFIG_FILE):
        config.load(CACHED_CONFIG_FILE)

    for name, (prompt, _, _) in config.get_entries():
        arg_parser.add_argument(f"--{name}", help=prompt)

    args = vars(arg_parser.parse_args(sys.argv[1:]))
    for name, _ in config.get_entries():
        val = args[name]
        if val is None:
            continue
        config.set_val(name, val)

    if not config.is_all_set:
        config.ask_interactive()
    assert config.is_all_set

    if not gcal.is_auth:
        gcal.auth(config.get_parsed_val('gcal_creds_path'),
                  config.get_parsed_val('gcal_token_path'))
    if not notion.is_auth:
        notion.auth(config.get_parsed_val('notion_token_path'))

    p = config.get_parsed_val('gcal_creds_path')
    if p != CACHED_GCAL_CREDS_PATH:
        shutil.copyfile(p, CACHED_GCAL_CREDS_PATH)

    p = config.get_parsed_val('gcal_token_path')
    if p != CACHED_GCAL_TOKEN_PATH:
        shutil.copyfile(p, CACHED_GCAL_TOKEN_PATH)

    p = config.get_parsed_val('notion_token_path')
    if p != CACHED_NOTION_TOKEN_PATH:
        shutil.copyfile(p, CACHED_NOTION_TOKEN_PATH)

    config.set_val('gcal_creds_path', CACHED_GCAL_CREDS_PATH)
    config.set_val('gcal_token_path', CACHED_GCAL_TOKEN_PATH)
    config.set_val('notion_token_path', CACHED_NOTION_TOKEN_PATH)

    config.dump(CACHED_CONFIG_FILE)


def do_sync() -> None:
    db = get_notion_active_db()
    field_col_map = config.get_parsed_val("field_col_map")
    cal_merge_map = config.get_parsed_val("cal_merge")
    col_const_list = config.get_parsed_val("col_const")

    # map gcal event id to notion database page id
    sync_token_map = DurableMap(DURABLE_MAP_PATH, "SYNC_TOKEN_MAP")

    # get from google calendar for events added or updated
    for cal in config.get_parsed_val("cal_list"):
        # table name must be sql-safe, so we use the hash value of the cal.name,
        # instead of use it directly
        id_map = DurableMap(
            DURABLE_MAP_PATH,
            f"ID_MAP_{hashlib.sha256(cal.name.encode('utf-8')).hexdigest()}")
        sync_token = sync_token_map.get(cal.name)
        time_min = None
        if sync_token is None:
            time_min = config.get_parsed_val("time_min")
        events_id_list, next_sync_token = cal.list_events_id(
            time_min=time_min, sync_token=sync_token)

        for eid in events_id_list:
            event = cal.get_event(eid)
            if event.is_deleted:
                db.delete_page(eid)
                id_map.delete(eid)
            else:
                pb = PageBuilder()

                #### Map Google Calendar fields to Notion Database columns ####
                # FIELDS supported:
                #   ["cal_name", "title", "time", "location", "description"]
                col = field_col_map.get("cal_name")
                if col is not None:
                    cal_name = cal.name
                    #### Redirect one calendar to another  ####
                    if cal_name in cal_merge_map:
                        cal_name = cal_merge_map[cal_name]
                    pb.add_column(col, cal_name)

                col = field_col_map.get("time")
                if col is not None:
                    pb.add_date(col.name, event.start, event.end)

                # "summary" looks less intuitive than "title" for end-users
                # so we call it "title", through it's actually called "summary"
                # in Google Calendar
                col = field_col_map.get("title")
                if col is not None:
                    val = event["summary"]
                    if val is not None:
                        pb.add_column(col, val)

                for field in ["location", "description"]:
                    col = field_col_map.get(field)
                    val = event[field]
                    if col is not None and val is not None:
                        pb.add_column(col, val)

                #### Add constant-value columns  ####
                for col, const in col_const_list:
                    pb.add_column(col, const)

                page = pb.build()
                page_id = id_map.get(eid)
                if page_id is None:
                    p = db.create_page(page)
                    assert p.is_instantiated
                    id_map.put(eid, p.id)
                else:
                    db.update_page(page_id, page)
        id_map.commit()
        id_map.close()
        sync_token_map.put(cal.name, next_sync_token, commit=True)
    sync_token_map.close()


if __name__ == "__main__":
    log_level = os.environ.get("SNOW_LOG_LEVEL")
    if log_level is not None:
        if log_level == "DEBUG":
            logging.basicConfig(level=logging.info)
        elif log_level == "INFO":
            logging.basicConfig(level=logging.INFO)
        elif log_level == "WARNING":
            logging.basicConfig(level=logging.WARNING)
        else:
            raise ValueError(f"Unknown log level: {log_level}")

    os.makedirs(DATA_DIR, exist_ok=True)
    load_config()
    do_sync()
