# coding:utf-8
from peewee import *
import time


db = SqliteDatabase('database.db')


class BaseModel(Model):
    class Meta:
        database = db

class Member(BaseModel):
    tg_id = IntegerField(unique=True)
    is_bot = BooleanField(default=False)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    updated_ = IntegerField(default=int(time.time()))

    @property
    def full_name(self):
        name = []
        if self.first_name:
            name.append(self.first_name)
        if self.last_name:
            name.append(self.last_name)
        return ' '.join(name)

    @property
    def call_name(self):
        if self.username:
            return '@%s' % self.username
        return self.full_name

class Chat(BaseModel):
    tg_id = IntegerField(unique=True)
    type = CharField(16)
    title = CharField()
    updated_ = IntegerField(default=int(time.time()))

class Message(BaseModel):
    member = ForeignKeyField(Member)
    chat = ForeignKeyField(Chat, null=True)
    text = TextField()
    sent_ = IntegerField(default=int(time.time()))

class Doorbell(BaseModel):
    chat = ForeignKeyField(Chat)
    member = ForeignKeyField(Member)
    joined = BooleanField(default=True)
    greeted = BooleanField(default=False)
    time_ = IntegerField(default=int(time.time()))
