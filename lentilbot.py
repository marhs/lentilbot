"""
This is a telegram bot made to check if the James Joyce Irish Pub has
their awesome lentils in the menu.
"""

import re
import logging
from datetime import date

import requests
import telegram
from telegram.ext import Updater
from lxml import html

import settings

logger = logging.getLogger()
logger.setLevel(logging.INFO)
TOKEN = settings.token


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
    logger.info("Lentils msg received")
    menu = get_menu()

    there_are_lentils, dish = lentils(menu, keyword=keyword)

    if there_are_lentils:
        msg = "¡Hoy hay {}! \nEl plato es ".format(keyword) + dish
    else:
        msg = "Hoy no hay lentejas :("

    try:
        bot.sendMessage(chat_id=update.message.chat_id, text=msg)
    except:
        logger.error("Error sending response to /lentils", exec_info=True)


def menu_command(bot, update):
    logger.info("Lentils msg received")
    menu = get_menu()
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
        logger.error("Error sending response to /menu", exec_info=True)


def start_command(bot, update):
    msg = """
    ¡Hola! Soy el bot de Lentejas de @helmetk para ver el menú
del James Joyce. Puedo comprobar si hay /lentejas o
enseñarte el /menu
    """
    try:
        bot.sendMessage(
            chat_id=update.message.chat_id,
            text=msg)
    except:
        logger.error("Error sending response to /start", exec_info=True)


def init(token):
    # Init the bot
    # bot = telegram.Bot(token=token)
    updater = Updater(token=token)
    dispatcher = updater.dispatcher

    dispatcher.addTelegramCommandHandler('lentejas', lentils_command)
    dispatcher.addTelegramCommandHandler('menu', menu_command)
    dispatcher.addTelegramCommandHandler('start', start_command)
    dispatcher.addTelegramCommandHandler('help', start_command)
    updater.start_polling()

init(TOKEN)
