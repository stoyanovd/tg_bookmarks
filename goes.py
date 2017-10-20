import logging
import os

from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, CommandHandler

from default_tg_bot.tg_conf import init_conf


#################################################

# TgBot some example command realizations

def start(bot, update):
    update.message.reply_text('Hello World!')


def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))
    # update.message


def echo(bot, update):
    msg = update.message.text

    ans = "I repeat." + os.linesep + msg
    # tg has restriction to 4096 symbols in one message
    ans = ans[:4096]
    bot.send_message(chat_id=update.message.chat_id, text=ans)


#################################################

# TgBot pipeline

def set_up_bot(conf):
    updater = Updater(conf.TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('hello', hello))

    dispatcher.add_handler(MessageHandler(Filters.text, echo))

    print("finish set up bot.")
    return updater


def start_webhooks(updater, conf):
    updater.start_webhook(listen="0.0.0.0",
                          port=conf.PORT,
                          url_path=str("") + conf.TOKEN)
    updater.bot.set_webhook(conf.WEBHOOK_URL_PREFIX + conf.TOKEN)


def start_polling(updater):
    updater.start_polling()


def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    conf = init_conf()
    updater = set_up_bot(conf)

    # start_webhooks(updater, conf)
    # OR
    start_polling(updater)

    print("before idle")
    updater.idle()
    print("after idle")


if __name__ == '__main__':
    main()
