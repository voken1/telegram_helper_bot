# coding:utf-8
from vn_db import *


db.connect()
db.create_tables([Member, Chat, Message, Doorbell])

print('Database: initialization complete!')
