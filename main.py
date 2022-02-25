import asyncio
import json
import random
from typing import List, Tuple, Optional

from datetime import datetime

import discord
from discord import Member, Message, VoiceState, VoiceChannel, TextChannel
from discord.ext import commands
from discord.ext.tasks import loop
from discord.ext.commands import Context

from configs import *
from errors import handle_errors
from functions import find, strdate2excel, strdate
from g0 import Google
from scoreboard import ScoreboardMessage, SCOREBOARD_SIGNATURE
from sheet import Sheet


bot = commands.Bot(command_prefix='ai-', status=discord.Status.dnd, activity=None)


lock_google = asyncio.Lock()


async def google_credentials():
    async with lock_google:
        return Google.auth(CREDENTIALS_FILEPATH, GOOGLE_TOKEN_FILEPATH)


async def scoreboard_message_lookup(channel: TextChannel) -> Optional[Message]:
    pins: List[Message] = await channel.pins()
    sorted_pins = sorted(pins, key=lambda it: it.created_at, reverse=True)
    return find(lambda it: ScoreboardMessage.is_resemble(it.clean_content), sorted_pins)


async def scoreboard_sheet_load(channel: TextChannel) -> Sheet:
    message = await scoreboard_message_lookup(channel)
    assert message is not None, f"Pinned message with scoreboard signature '{SCOREBOARD_SIGNATURE}' not found"
    scoreboard = ScoreboardMessage.parse(message)
    document_id = Google.get_sheet_id(scoreboard.url)
    # sheet.fix_flags([TIME_CODES_COLUMN_INDEX])  # not yet needed cus of render option
    credentials = await google_credentials()
    return Google(credentials).load_sheet(document_id, scoreboard.cells)


async def get_voice_channel(ctx: Context) -> VoiceChannel:
    voice: VoiceState = ctx.message.author.voice
    assert voice is not None, "Not connected to any voice channel, please connect"
    return voice.channel


async def get_voice_desc(ctx: Context) -> Tuple[VoiceChannel, List[Member]]:
    voice_channel = await get_voice_channel(ctx)
    members: List[Member] = voice_channel.members
    assert not CHECK_ON_EMPTY_VOICE_CHANNEL or len(members) != 0, \
        f"You are the only one in the voice channel '{voice_channel.name}' or nobody in channel, please reconnect"
    return voice_channel, members


@loop(seconds=REFRESH_GOOGLE_API_TOKEN_TIME)
async def refresh_token():
    await bot.wait_until_ready()
    print(f"Refresh google credentials token {datetime.now()}")

    await bot.change_presence(activity=discord.Game(name="Refresh tokens"))

    await google_credentials()  # I hope this will work

    await bot.change_presence(activity=None)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord at {datetime.now()}!')


@bot.command(
    name="выбери-кто-соберет-таймкоды",
    help="Выбирает пользователя случайным образом у кого выставлен <V> в таймкодах"
)
@commands.has_role("root")
@handle_errors(bot)
async def choose_timecoder(ctx: Context, score: int = 2):
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Выбираю, кто соберет таймкоды"))

    voice_channel, members = await get_voice_desc(ctx)

    sheet = await scoreboard_sheet_load(ctx.channel)

    acquired_timecoders = sheet.get_timecoders()
    assert acquired_timecoders, f"Nobody want to be timecoder"

    present_users = [it.display_name for it in members]

    present_timecoders = list(set(acquired_timecoders) & set(present_users))
    assert present_timecoders, f"All possible timecoders are absent :("

    timecoder = random.choice(present_timecoders)
    member = next(it for it in members if it.display_name == timecoder)

    date = strdate(ctx.message.created_at)

    await ctx.reply(f"Исскуственный интелект назначил тебя {member.mention} отвественным за таймкоды **{date}**, "
                    f"по {voice_channel.mention}. Ты получишь +{score} баллов, если успешно справишься "
                    f"с задачей и -1 в противном случае")


@bot.command(
    name="отметь-кто-тут",
    help="Обновляет score пользователей, в голосовом канале"
)
@commands.has_role("root")
@handle_errors(bot)
async def update_score(ctx: Context, date: Optional[str] = None, score: int = 1):
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Отмечаю, кто сидит в голосовом канале..."))

    voice_channel, members = await get_voice_desc(ctx)

    assert score > 0, f"This is unfair to add {score}"

    sheet = await scoreboard_sheet_load(ctx.channel)

    date = date or strdate(ctx.message.created_at)
    excel_date = strdate2excel(date)

    assert sheet.is_header_exists(excel_date), f"Date '{date}' not found in table headers"

    lines = []
    for member in members:
        new_score = sheet.add_score(member.display_name, excel_date, score)
        if new_score is not None:
            string = f"- Новый score пользователя {member.mention}: {new_score}"
        else:
            print(f"User not found: {member.display_name}")
            string = f"- Пользователь {member.mention} не был найден в Scoreboard :("
        lines.append(string)

    if not DRY_SHEET_RUN:
        credentials = await google_credentials()
        Google(credentials).store_sheet(sheet)

    message = f"Обновленный рейтинг за {date} по данным из {voice_channel.mention}:\n" + "\n".join(lines)

    await ctx.reply(message)


def discord_get_token(token_path: str) -> str:
    with open(token_path, "rt") as file:
        data = json.loads(file.read())
    return data["token"]


def main():
    refresh_token.start()

    token = discord_get_token("discord.json")
    bot.run(token)


if __name__ == "__main__":
    main()