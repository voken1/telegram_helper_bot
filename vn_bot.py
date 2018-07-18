# coding:utf-8
import time
import telepot
import vn_match
import vn_data.replies
from vn_data import conf
from vn_db import *
from pprint import pprint
from telepot.loop import MessageLoop


class TgBot:
    def __init__(self, token, lang='en'):
        self._token = token
        self._lang = lang
        self._bot = telepot.Bot(self._token)
        self._me = self.bot.getMe()
        self._chat = None
        self._member = None
        self.prt()
        self.message_loop()

    @property
    def bot(self):
        return self._bot

    @property
    def token(self):
        return self._token

    @property
    def lang(self):
        return self._lang

    def prt(self):
        pprint(self._me)

    def message_loop(self):
        MessageLoop(self.bot, self.on_message).run_as_thread(relax=conf.bot_relax)

    def on_message(self, msg):
        chat = self._save_chat(msg['chat'], msg['date'])
        member = self._save_member(msg['from'], msg['date'])

        content_type, chat_type, chat_id = telepot.glance(msg)

        print('\n\n--- [ %s ] ---\n' % content_type, chat_type, chat_id)
        pprint(msg)

        if content_type == 'text':
            self._on_chat_message_text(chat, member, msg)

        elif chat_type in ['supergroup', 'group'] and content_type == 'new_chat_member':
            # if i am the one
            if self._me['id'] == msg['new_chat_member']['id']:
                return self._on_join_a_group(chat)

            # an user joined
            return self._on_new_chat_member(chat, msg)

        elif chat_type in ['supergroup', 'group'] and content_type == 'left_chat_member':
            self._on_left_chat_member(chat, msg)

    def _save_chat(self, c, d):
        chat_dict = self._get_defaults_dict(
                source=c,
                keys={
                    'title': 'title',
                    'username': 'title',
                },
                existing={
                    'type': c['type'],
                    'updated_':d,
                },
            )

        # chat get_or_create
        chat, created = Chat.get_or_create(
            tg_id=c['id'],
            defaults=chat_dict,
        )

        # update
        need_update = False
        if chat.type != chat_dict.get('type'):
            chat.type = chat_dict.get('type')
            need_update = True
        if chat.title != chat_dict.get('title'):
            chat.title = chat_dict.get('title')
            need_update = True
        if need_update:
            chat.updated_ = d
            chat.save()

        # return
        return chat

    def _save_member(self, m, d):
        member_dict = self._get_defaults_dict(
            source=m,
            keys={
                'username': 'username',
                'is_bot': 'is_bot',
                'first_name': 'first_name',
                'last_name': 'last_name',
            },
            existing={
                'updated_': d,
            },
        )

        # member get_or_create
        member, created = Member.get_or_create(
            tg_id=m['id'],
            defaults=member_dict,
        )

        # update
        need_update = False
        if member.username != member_dict.get('username'):
            member.username = member_dict.get('username')
            need_update = True
        if member.first_name != member_dict.get('first_name'):
            member.first_name = member_dict.get('first_name')
            need_update = True
        if member.last_name != member_dict.get('last_name'):
            member.last_name = member_dict.get('last_name')
            need_update = True
        if need_update:
            member.updated_ = d
            member.save()

        # return
        return member

    @staticmethod
    def _get_defaults_dict(source, keys, existing=None):
        # existing
        if existing is None:
            result = {}
        else:
            result = existing

        # keys
        for i in keys:
            if i in source.keys():
                result[keys[i]] = source[i]

        # return
        return result

    def _on_chat_message_text(self, chat, member, msg):
        # welcome
        if msg['text'] in ['w', 'welcome']:
            self.bot.deleteMessage((chat.tg_id, msg['message_id']))
            self._hello(chat)

        # vision summary
        elif msg['text'] in ['s', 'summary']:
            self.bot.deleteMessage((chat.tg_id, msg['message_id']))
            self._send_messages(chat, vn_data.replies.summaries[self.lang])

        # save message text
        message = Message.create(
            member_id=member.id,
            chat_id=chat.id,
            chat_message_id=msg['message_id'],
            text=msg['text'],
            sent_=msg['date'],
        )

        # match replies
        replies = vn_match.get_matched_replies(msg['text'], self._lang)
        if replies:
            self._send_messages(chat, replies)

    def _on_join_a_group(self, chat):
        # I am a BOT
        self._send_messages(chat, vn_data.replies.bot_here[self._lang])
        return

    def _on_new_chat_member(self, chat, msg):
        member = self._save_member(msg['new_chat_member'], msg['date'])
        doorbell = Doorbell.create(
            chat_id=chat.id,
            member_id=member.id,
            joined=True,
            time_=msg['date'],
        )

        # If there are too many doorbells in a short time, erase the footprint.
        doorbells = Doorbell.select().where((Doorbell.chat == chat) & (Doorbell.joined == True))
        if (doorbells.count() > 2 and conf.doorbells_batch_limit_period > msg['date'] - doorbells[-2].time_
                and doorbells.count() > conf.doorbells_batch_limit):
            self.bot.deleteMessage((chat.tg_id, msg['message_id']))

        # or say hello
        else:
            self._hello(chat)

        return

    def _on_left_chat_member(self, chat, msg):
        member = self._save_member(msg['left_chat_member'], msg['date'])
        doorbell = Doorbell.create(
            chat_id=chat.id,
            member_id=member.id,
            joined=False,
            time_=msg['date'],
        )

        # erase footprint.
        self.bot.deleteMessage((chat.tg_id, msg['message_id']))
        return

    def _send_messages(self, chat, messages):
        for row in messages:
            if isinstance(row, str):
                self.bot.sendMessage(chat.tg_id, row)
                time.sleep(len(row) / conf.chars_per_second)
            elif isinstance(row, dict):
                self.bot.sendMessage(chat.tg_id, 'dict...')
            elif isinstance(row, list):
                self._send_messages(chat, row)

    def _hello(self, chat):
        doorbells = Doorbell.select().where(
            (Doorbell.chat == chat)
            & (Doorbell.joined == True)
            & (Doorbell.greeted == False))

        if doorbells.count() < conf.hello_mentioned_limit:
            names = []
            for doorbell in doorbells:
                names.append(doorbell.member.call_name)
                doorbell.greeted = True
                doorbell.save()
            self.bot.sendMessage(chat.tg_id, vn_data.replies.hello[self.lang] % '\n'.join(names))
        else:
            self.bot.sendMessage(chat.tg_id, vn_data.replies.hello2all[self.lang])

        # summaries
        self._send_messages(chat, vn_data.replies.summaries[self.lang])
