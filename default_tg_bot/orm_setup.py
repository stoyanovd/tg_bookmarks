from enum import Enum, IntEnum, auto

from pony.orm import *

# def init_our_models():
db = Database()


class WorkStateEnum(IntEnum):
    Nothing = auto()
    Add_Url = auto()
    Add_Name = auto()
    Add_Tags = auto()


class Chat(db.Entity):
    chat_id = Required(int)
    bm = Set('Bookmark')
    state = Required(WorkStateEnum, default=WorkStateEnum.Nothing)
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

# db.bind('sqlite', ':memory:')
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
# db.bind(provider='postgres', user='', password='', host='', database='')


db.generate_mapping(create_tables=True)
