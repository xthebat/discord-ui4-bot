import asyncio
import functools
import json
import random
from typing import List, Tuple, Optional

import discord
from discord.ext.commands import Context, Bot

ATTACHMENT_SIGNATURE = "<ATTACHMENT>"

ERROR_PHRASES = [
    "Что-то пошло не так, разбирайся...",
    "Давай так больше не будем делать?",
    "Ты хочешь выполнить команду, но делаешь это без уважения:",
    "Вот не делай так больше, ок?",
    "Отчислен от трех до четырех раз!",
    "Сложно без ошибок написать, да?",
    "Не работает, попробуем ещё раз?",
    "Да !@#$%, как так можно-то код писать?",
    "С вашим кодом явно что-то не так",
    "Почему код писал кто-то другой, а не работаю теперь я?"
]


working_lock = asyncio.Lock()


def attachments(*args):
    data = json.dumps(args)
    return f"{ATTACHMENT_SIGNATURE}{data}"


def _parse_assert(string: str) -> Tuple[str, List[str]]:
    if ATTACHMENT_SIGNATURE in string:
        message, _, data = string.partition(ATTACHMENT_SIGNATURE)
        attaches = json.loads(data)
        return message, attaches
    else:
        return string, list()


def playgame(bot: Bot, activity):

    def decorator(function):

        @functools.wraps(function)
        async def wrapped(*args, **kwargs):
            await bot.wait_until_ready()

            # if bot command wrapped
            ctx: Optional[Context] = args[0] if len(args) > 0 and type(args[0]) == Context else None

            if ctx is not None and ctx.author == bot.user:
                return None

            async with working_lock:

                await bot.change_presence(activity=activity)

                try:
                    await function(*args, **kwargs)
                except Exception as error:
                    if ctx is not None:
                        phrase = random.choice(ERROR_PHRASES)
                        message, attaches = _parse_assert(str(error))
                        string = '\n'.join(attaches)
                        reply = f"{phrase} ```{message}``` {string}"
                        await ctx.reply(reply)

                    raise
                finally:
                    await bot.change_presence(activity=None)

        return wrapped

    return decorator
