import logging
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

from default_tg_bot.tg_conf import init_conf
conf = init_conf()

from pony.orm import commit
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler

from pony import orm
import default_tg_bot.orm_setup
from default_tg_bot.orm_setup import Chat, Bookmark, Tag
from default_tg_bot.orm_setup import WorkStateEnum


#################################################

# TgBot some example command realizations

def start(bot, update):
    update.message.reply_text('Hello World!')


def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


#################################################


@orm.db_session
def get_chat(chat_id, update):
    chat = Chat.get(chat_id=chat_id)
    if not chat:
        chat = Chat(chat_id=chat_id)
        update.message.reply_text("Hi in new chat.")
    commit()
    return chat


@orm.db_session
def get_bm(chat, msg, update):
    if Bookmark.get(url=msg):
        print("I already have this link. It will be rewritten.")
        bm = Bookmark.get(url=msg)
        update.message.reply_text("I already have this link. It will be rewritten.")
    else:
        print("I create new bm.")
        bm = Bookmark(url=msg, owner=chat)
        update.message.reply_text("I create new bm.")
    commit()
    return bm


@orm.db_session
def com_handler_add_bm_get_chat(bot, update):
    chat_id = update.message.chat.id
    print("I get chat_id: " + str(chat_id))
    chat = get_chat(chat_id, update)

    chat.state = int(WorkStateEnum.Add_Url)
    update.message.reply_text("Please write url:")


@orm.db_session
def mid_handler_add_bm_get_url(msg, chat, update):
    bm = get_bm(chat, msg, update)

    update.message.reply_text("Please write (optional) name for bookmark:")
    chat.state = int(WorkStateEnum.Add_Name)
    chat.current_bm = bm.url


@orm.db_session
def mid_handler_add_bm_get_name(msg, chat, update):
    bm = Bookmark.get(url=chat.current_bm)
    assert bm
    bm.name = msg

    update.message.reply_text("Please write a lot of tags separated by spaces:")
    chat.state = int(WorkStateEnum.Add_Tags)


@orm.db_session
def get_tag(name):
    tag = Tag.get(name=name)
    if not tag:
        tag = Tag(name=name)
    commit()
    return tag


@orm.db_session
def mid_handler_add_bm_add_tags(msg, chat, update):
    bm = Bookmark.get(url=chat.current_bm)
    tags_name = msg.split(' ')
    tags = [get_tag(s) for s in tags_name]
    bm.tags = tags

    update.message.reply_text("We add these tags:")
    update.message.reply_text(str([tag.name for tag in bm.tags]))

    update.message.reply_text("Finish adding bookmark.")
    chat.state = int(WorkStateEnum.Nothing)


command_resolver = {
    int(WorkStateEnum.Nothing): lambda *args: 1,
    int(WorkStateEnum.Add_Url): mid_handler_add_bm_get_url,
    int(WorkStateEnum.Add_Name): mid_handler_add_bm_get_name,
    int(WorkStateEnum.Add_Tags): mid_handler_add_bm_add_tags,
}


@orm.db_session
def all_common_messages_handler(bot, update):
    chat_id = update.message.chat.id
    print("I get chat_id: " + str(chat_id))
    chat = get_chat(chat_id, update)

    msg = update.message.text

    callback = command_resolver[chat.state]
    if callback:
        callback(msg, chat, update)

        # bot.send_message(chat_id=update.message.chat_id, text=ans)


@orm.db_session
def com_handler_list(bot, update):
    chat_id = update.message.chat.id
    print("I get chat_id: " + str(chat_id))
    chat = get_chat(chat_id, update)

    ans = ""
    for bm in chat.bm:
        ans += "url=" + bm.url + os.linesep + "(name=" + bm.name + ")" \
               + os.linesep \
               + " ".join([tag.name for tag in bm.tags]) \
               + os.linesep

    update.message.reply_text("----------")
    if ans:
        update.message.reply_text(ans)
        update.message.reply_text("----------")


@orm.db_session
def com_handler_stop(bot, update):
    chat_id = update.message.chat.id
    print("I get chat_id: " + str(chat_id))
    chat = get_chat(chat_id, update)

    chat.state = int(WorkStateEnum.Nothing)
    update.message.reply_text("Ok. All is finished.")


#################################################

# TgBot pipeline

def set_up_bot(conf):
    updater = Updater(conf.TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))

    dispatcher.add_handler(CommandHandler('hello', hello))

    dispatcher.add_handler(CommandHandler('add', com_handler_add_bm_get_chat))

    dispatcher.add_handler(CommandHandler('stop', com_handler_stop))
    dispatcher.add_handler(CommandHandler('list', com_handler_list))

    dispatcher.add_handler(MessageHandler(Filters.text, all_common_messages_handler))

    print("finish set up bot.")
    return updater


#################################################

"""
hello - Test it works
add - Add new bookmark
stop - Stop asking for details and finish
list - List all bookmarks
"""


#################################################

def start_webhooks(updater, conf):
    updater.start_webhook(listen="0.0.0.0",
                          port=conf.PORT,
                          url_path=str("") + conf.TOKEN)
    updater.bot.set_webhook(conf.WEBHOOK_URL_PREFIX + conf.TOKEN)


def start_polling(updater):
    updater.start_polling()


def main():
    updater = set_up_bot(conf)

    # for heroku
    start_webhooks(updater, conf)
    # OR
    # for run from your computer
    # start_polling(updater)

    print("before idle")
    updater.idle()
    print("after idle")


if __name__ == '__main__':
    main()
