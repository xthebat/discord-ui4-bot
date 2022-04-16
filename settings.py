import os

import pytz

DRY_SHEET_RUN = False

CHECK_ON_EMPTY_VOICE_CHANNEL = True

BOT_CONFIG_PATH = "configs"

DISCORD_CONFIG_FILEPATH = os.path.join(BOT_CONFIG_PATH, "discord.json")
GITHUB_CONFIG_FILEPATH = os.path.join(BOT_CONFIG_PATH, "github.json")
GOOGLE_CREDENTIALS_FILEPATH = os.path.join(BOT_CONFIG_PATH, "google.json")

CYRILLIC_ALPHABET = set("аАбБвВгГдДеЕёЁжЖзЗиИйЙкКлЛмМнНоОпПрРсСтТуУфФхХцЦчЧшШщЩъЪыЫьЬэЭюЮяЯ")
SPACE_SET = set(" ")

DAILY_TASK_CHECK_PERIOD = 60

TIMEZONE = "Europe/Moscow"

TZ_INFO = pytz.timezone(TIMEZONE)
