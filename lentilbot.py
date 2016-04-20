"""
This is a telegram bot made to check if the James Joyce Irish Pub has
their awesome lentils in the menu.
"""

import re
import pickle
import logging
from datetime import date

import requests
import telegram
from telegram.ext import Updater
from lxml import html

import settings

TOKEN = settings.token
logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%Y/%m/%d %I:%M:%S %p',
    filename='basic.log',
    level=logging.INFO,
)

logging.basicConfig(filename='basic.log', level=logging.DEBUG)


def get_dish_data(dishes):
    first = []
    for dish in dishes:
        first.append(dish.text_content())
    return first


def get_menu():
    page = requests.get('http://www.jamesjoycemadrid.com/')
    tree = html.fromstring(page.content)

    div_first, div_second = tree.xpath('//div[@class="cuerpoMenuDia"]/ul')
    first_dishes_li = div_first[1:]
    second_dishes_li = div_second[1:]

    return {'first': get_dish_data(first_dishes_li),
            'second': get_dish_data(second_dishes_li)}


def lentils(menu, keyword='ternera'):
    for key in menu:
        for dish in menu[key]:
            words = re.findall('[a-z]+', dish.lower())
            if keyword in words:
                return (True, dish)
    return (False, '')


def lentils_command(bot, update):
    keyword = 'lentejas'
    logging.info("/lentils command received from {}".format(
        update.message.from_user.username))
    menu = read_menu()

    there_are_lentils, dish = lentils(menu, keyword=keyword)

    if there_are_lentils:
        msg = "¡Hoy hay {}! \nEl plato es ".format(keyword) + dish
    else:
        msg = "Hoy no hay lentejas :("

    try:
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    except:
        logging.error("Error sending response to /lentils", exec_info=True)


def menu_command(bot, update):
    logging.info("/menu command received from {}".format(
        update.message.from_user.username))
    menu = read_menu()
    msg = "Hoy es {}\n*Primer plato*\n".format(
        date.today().strftime('%Y-%m-%d'))

    for dish in menu['first']:
        msg += " - {} \n".format(dish)
    msg += "\n*Segundo plato*\n"
    for dish in menu['second']:
        msg += " - {} \n".format(dish)

    try:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=msg,
                        parse_mode=telegram.ParseMode.MARKDOWN)
    except:
        logging.error("Error sending response to /menu", exec_info=True)


def start_command(bot, update):
    msg = """
    ¡Hola! Soy el bot de Lentejas de @helmetk para ver el menú
del James Joyce. Puedo comprobar si hay /lentejas o
enseñarte el /menu
    """
    logging.info("/start - /help command received from {}".format(
        update.message.from_user.username))
    try:
        bot.sendMessage(
            chat_id=update.message.chat_id,
            text=msg)
    except:
        logging.error("Error sending response to /start", exec_info=True)


def update_menu(bot):
    logging.info("Updating menu")
    menu = get_menu()
    output = open('menu.pkl', 'wb')
    pickle.dump(menu, output)
    output.close()
    return menu


def read_menu():
    try:
        pkl_file = open('menu.pkl', 'rb')
        menu = pickle.load(pkl_file)
    except:
        logging.warning("Couldn't read menu")
        menu = update_menu()
    return menu


def init(token):
    # Init the bot
    # bot = telegram.Bot(token=token)
    logging.info("Starting bot")
    updater = Updater(token=token)
    dispatcher = updater.dispatcher
    update_menu(None)

    job_queue = updater.job_queue
    job_queue.put(update_menu, 60 * 60)
    dispatcher.addTelegramCommandHandler('lentejas', lentils_command)
    dispatcher.addTelegramCommandHandler('menu', menu_command)
    dispatcher.addTelegramCommandHandler('start', start_command)
    dispatcher.addTelegramCommandHandler('help', start_command)
    updater.start_polling()

init(TOKEN)
