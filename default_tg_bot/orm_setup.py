import os
from enum import Enum, IntEnum, auto

from pony.orm import *

# def init_our_models():
db = Database()


class WorkStateEnum(IntEnum):
    Nothing = 0
    Add_Url = 1
    Add_Name = 2
    Add_Tags = 3


class Chat(db.Entity):
    chat_id = Required(int)
    bm = Set('Bookmark')
    state = Required(int, default=0)
    current_bm = Optional(str, nullable=True)


class Bookmark(db.Entity):
    url = Required(str)
    name = Optional(str)
    tags = Set(lambda: Tag, nullable=True)
    owner = Required('Chat')
    # optional_owner = Optional(Chat, nullable=True, reverse='current_bm')


class Tag(db.Entity):
    name = Required(str)
    bookmarks = Set(Bookmark)


sql_debug(True)

# db.bind(provider='sqlite', filename='database.sqlite', create_db=True)

from urllib.parse import urlparse

result = urlparse(os.environ['DATABASE_URL'])
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname

db.bind(provider='postgres', user=username, password=password, host=hostname, database=database)

db.generate_mapping(create_tables=True)
