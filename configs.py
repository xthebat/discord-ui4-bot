import os
from os.path import expanduser

import pytz

USER_HOME_DIR = expanduser("~")

DRY_SHEET_RUN = False

CHECK_ON_EMPTY_VOICE_CHANNEL = True

BOT_CONFIG_DIR = ".discord-iu4-bot"

BOT_CONFIG_PATH = os.path.join(USER_HOME_DIR, BOT_CONFIG_DIR)

DISCORD_CONFIG_FILEPATH = os.path.join(BOT_CONFIG_PATH, "discord.json")
GOOGLE_CREDENTIALS_FILEPATH = os.path.join(BOT_CONFIG_PATH, "credentials.json")
GOOGLE_TOKEN_FILEPATH = os.path.join(BOT_CONFIG_PATH, "google.json")

CYRILLIC_ALPHABET = set("аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОпПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ")
SPACE_SET = set(" ")

DAILY_TASK_CHECK_PERIOD = 60

TIMEZONE = "Europe/Moscow"

TZ_INFO = pytz.timezone(TIMEZONE)
