# coding:utf-8
import vn_console
from vn_data import conf
from vn_bot import TgBot


bots = []
for bot in conf.bots:
    print('Starting BOT:', bot['token'].split(':')[0])
    bots.append(TgBot(token=bot['token'], lang=bot['lang']))

a = bots[0]


vn_console.embed(banner='Listening....')
