# coding:utf-8
redis_conf = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0,
    'decode_responses': True,
}


bots = [
    {'token': 'BOT_TOKEN', 'lang': 'en'},
]


bot_relax = 3
chars_per_second = 15
welcome_interval_seconds = 3600
seems_like_invited_by_a_robot_limit = 1
many_new_chat_members_limit = 6
