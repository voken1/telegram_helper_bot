# coding:utf-8
import time
import telepot
import vn_match
import vn_data.replies
from vn_data import conf
from vn_cache import Cache
from pprint import pprint
from telepot.loop import MessageLoop


class TgBot:
    def __init__(self, token, lang='en'):
        self._cache = Cache()
        self._token = token
        self._lang = lang
        self._bot = telepot.Bot(self._token)
        self._me = self.bot.getMe()
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
        content_type, chat_type, chat_id = telepot.glance(msg)

        print('\n\n--- [ %s ] ---\n' % content_type, chat_type, chat_id)
        pprint(msg)

        if content_type == 'text':
            self._on_chat_message_text(chat_id, msg)
        elif chat_type in ['supergroup', 'group'] and content_type == 'new_chat_member':
            self._on_new_chat_member(chat_id, msg)
        elif chat_type in ['supergroup', 'group'] and content_type == 'left_chat_member':
            self._on_left_chat_member(chat_id, msg)

    def _on_chat_message_text(self, chat_id, msg):
        # welcome
        if msg['text'] in ['w']:
            self._welcome(chat_id)

        # vision summary
        elif msg['text'] in ['vn', 'vision']:
            self._summary(chat_id)

        elif 'del' in msg['text']:
            self.bot.deleteMessage((chat_id, msg['message_id']))

        # match replies
        replies = vn_match.get_matched_replies(msg['text'], self._lang)
        if replies:
            for row in replies:
                self.bot.sendMessage(chat_id, row)
                time.sleep(len(row)/conf.chars_per_second)

    def _on_new_chat_member(self, chat_id, msg):
        if self._me['id'] == msg['new_chat_member']['id']:
            self.bot.sendMessage(chat_id, 'hello everyone, i\'m a bot.')
            return True

        new_members = self._new_chat_members(chat_id=chat_id)

        latest_date_key = self._get_latest_new_chat_member_joined_date_cache_key(chat_id)
        latest_date = self._cache.get(latest_date_key)
        if latest_date is None:
            latest_date = 0

        # nearly & seems like invited by a robot ? pend and erase the footprint
        if (new_members
                and conf.welcome_interval_seconds > msg['date'] - latest_date
                and conf.seems_like_invited_by_a_robot_limit < len(new_members)):

            # pend
            self._new_chat_member_append(chat_id=chat_id, date=msg['date'], member=msg['new_chat_member'])

            # erase the footprint
            self.bot.deleteMessage((chat_id, msg['message_id']))

        # or hello
        else:
            self.bot.sendMessage(chat_id, vn_data.replies.hello[self.lang] % self._member2name(msg['new_chat_member']))
            for row in vn_data.replies.summaries[self.lang]:
                self.bot.sendMessage(chat_id, row)
                time.sleep(len(row) / conf.chars_per_second)

        # refresh latest_date cache
        self._cache.set(latest_date_key, msg['date'])

    def _on_left_chat_member(self, chat_id, msg):
        # self.bot.deleteMessage((chat_id, msg['message_id']))
        pass

    @staticmethod
    def _member2name(member):
        if 'username' in member:
            return '@%s' % member['username']

        name = []

        if 'first_name' in member:
            name.append(member['first_name'])

        if 'last_name' in member:
            name.append(member['last_name'])

        return ' '.join(name)

    def _get_new_chat_members_cache_key(self, chat_id):
        return 'bot%d_chat%d_new_chat_members' % (self._me['id'], chat_id)

    def _get_latest_new_chat_member_joined_date_cache_key(self, chat_id):
        key = 'bot%d_chat%d_latest_new_chat_member_joined_date' % (self._me['id'], chat_id)
        return key

    def _new_chat_members(self, chat_id):
        new_members = self._cache.get(self._get_new_chat_members_cache_key(chat_id))
        if new_members is None:
            new_members = []

        return new_members

    def _in_new_chat_members(self, member_id, chat_id):
        new_members = self._new_chat_members(chat_id=chat_id)

        for row in new_members:
            if row['member']['id'] == member_id:
                return True
        return False

    def _new_chat_member_find(self, chat_id, member_id):
        new_members = self._new_chat_members(chat_id=chat_id)

        for row in new_members:
            if row['member']['id'] == member_id:
                return row
        return False

    def _new_chat_member_append(self, chat_id, date, member):
        new_members = self._new_chat_members(chat_id=chat_id)

        # add if new
        if not self._in_new_chat_members(member['id'], chat_id):
            new_members.append({
                'date': date,
                'member': member,
            })
            self._cache.set(self._get_new_chat_members_cache_key(chat_id), new_members)

        # return list
        return new_members

    def _new_chat_member_remove(self, chat_id, member_ids):
        new_members = self._new_chat_members(chat_id=chat_id)

        for row in new_members:
            if row['member']['id'] in member_ids:
                new_members.remove(row)

        self._cache.set(self._get_new_chat_members_cache_key(chat_id), new_members)

        return new_members

    def _new_chat_members_before(self, chat_id, date):
        members = []
        for member in self._new_chat_members(chat_id):
            if member['date'] <= date:
                members.append(member)
        return members

    def _new_chat_members_after(self, chat_id, date):
        members = []
        for member in self._new_chat_members(chat_id):
            if member['date'] >= date:
                members.append(member)
        return members

    def _welcome(self, chat_id):
        new_members = self._new_chat_members(chat_id)

        # say hello to every new members if not too many
        if new_members and len(new_members) < conf.many_new_chat_members_limit:
            names = []
            for rows in new_members:
                names.append(self._member2name(rows['member']))
            self.bot.sendMessage(chat_id, vn_data.replies.hello[self.lang] % '\n'.join(names))
        else:
            self.bot.sendMessage(chat_id, vn_data.replies.hello2all[self.lang])

        # empty new_members pool
        self._cache.set(self._get_new_chat_members_cache_key(chat_id), [])

        # vision summary
        self._summary(chat_id)

    def _summary(self, chat_id):
        for row in vn_data.replies.summaries[self.lang]:
            self.bot.sendMessage(chat_id, row)
            time.sleep(len(row) / conf.chars_per_second)

