import asyncio
import json
import logging
import os
import sys
import time
from functools import wraps
from inspect import getfullargspec
from os import environ
from sys import exit as sysexit
from traceback import format_exc

import spamwatch
import telegram.ext as tg
from arq import ARQ
from Abg import patch  # type: ignore
from aiohttp import ClientSession
from pyrogram import Client
from pyrogram.errors import ChannelInvalid, PeerIdInvalid
from pyrogram.types import Message
from telegram import Chat
from telegraph import Telegraph
from telethon import TelegramClient
from telethon.sessions import MemorySession

StartTime = time.time()


def get_user_list(__init__, key):
    with open(f"{os.getcwd()}/Exon/{__init__}", "r") as json_file:
        return json.load(json_file)[key]


FORMAT = "[ᴇxᴏɴ] %(message)s"
logging.basicConfig(
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
    format=FORMAT,
    datefmt="[%X]",
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

LOGGER = logging.getLogger("[ᴇxᴏɴ]")
LOGGER.info("Exon is starting...")

try:
    if environ.get("ENV"):
        from config import Config
    else:
        from config import Development as Config
except Exception as ef:
    LOGGER.error(ef)
    LOGGER.error(format_exc())
    sysexit(1)

if sys.version_info < (3, 8):
    LOGGER.error("Python 3.8+ required.")
    sys.exit(1)


TOKEN = Config.TOKEN
OWNER_ID = int(Config.OWNER_ID)
API_ID = Config.API_ID
API_HASH = Config.API_HASH
SPAMWATCH_API = Config.SPAMWATCH_API
ARQ_API_URL = "http://arq.hamker.in"
ARQ_API_KEY = Config.ARQ_API_KEY

if not SPAMWATCH_API:
    sw = None
    LOGGER.warning("SpamWatch API missing.")
else:
    try:
        sw = spamwatch.Client(SPAMWATCH_API)
    except Exception:
        sw = None
        LOGGER.warning("Cannot connect to SpamWatch.")

defaults = tg.Defaults(run_async=True)

updater = tg.Updater(
    token=TOKEN,
    use_context=True,
    workers=8,
)

dispatcher = updater.dispatcher

telethn = TelegramClient(MemorySession(), API_ID, API_HASH)

session_name = TOKEN.split(":")[0]

Abishnoi = Client(
    session_name,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN,
    in_memory=True,
)

aiohttpsession = ClientSession()
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

loop = asyncio.get_event_loop()

apps = [Abishnoi]

print("[INFO]: Getting bot info...")
BOT_ID = dispatcher.bot.id
BOT_NAME = dispatcher.bot.first_name
BOT_USERNAME = dispatcher.bot.username


async def eor(msg: Message, **kwargs):
    func = msg.edit_text if msg.from_user and msg.from_user.is_self else msg.reply
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})
