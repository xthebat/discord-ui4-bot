from wrapper import attachments
from dataclasses import dataclass
from typing import Optional

import validators
from discord import Message

from functions import int_or_else

SCOREBOARD_SIGNATURE = "**Сообщение с описанием Scoreboard**"
SCOREBOARD_ITEM_MARKER = "- "
SCOREBOARD_ITEM_SEP = ":"


SCOREBOARD_URL_NAME = "Ссылка"
SCOREBOARD_CELLS_NAME = "Столбцы"
SCOREBOARD_YEAR_NAME = "Год"


@dataclass
class ScoreboardMessage(object):
    url: str
    cells: str
    year: int

    @staticmethod
    def is_resemble(content: str) -> bool:
        return content.startswith(SCOREBOARD_SIGNATURE)

    @classmethod
    def parse(cls, message: Message) -> "ScoreboardMessage":
        content: str = message.clean_content

        assert content.startswith(SCOREBOARD_SIGNATURE), f"Invalid scoreboard message signature: {message.mentions}"

        content = content.lstrip(SCOREBOARD_SIGNATURE).lstrip()

        tokens = dict()
        for line in filter(lambda it: it.strip(), content.splitlines()):
            assert line.startswith(SCOREBOARD_ITEM_MARKER), f"Invalid scoreboard item: {line}"
            name, separator, value = line.lstrip(SCOREBOARD_ITEM_MARKER).partition(SCOREBOARD_ITEM_SEP)
            assert separator == SCOREBOARD_ITEM_SEP, f"Invalid scoreboard item: {line}"
            tokens[name] = value.strip()

        url = tokens.get(SCOREBOARD_URL_NAME, None)
        cells = tokens.get(SCOREBOARD_CELLS_NAME, None)
        year_str = tokens.get(SCOREBOARD_YEAR_NAME, None)

        assert url is not None, f"{SCOREBOARD_URL_NAME} not found {attachments(message.jump_url)}"
        assert cells is not None, f"{SCOREBOARD_CELLS_NAME} not found {attachments(message.jump_url)}"
        assert year_str is not None, f"{SCOREBOARD_YEAR_NAME} not found {attachments(message.jump_url)}"

        year = int_or_else(year_str)

        assert year is not None, f"Invalid year format: {year_str}"

        assert validators.url(url), f"Invalid URL format: {url}"

        return ScoreboardMessage(url, cells, year)

    @classmethod
    def parse_or_none(cls, message: Message) -> Optional["ScoreboardMessage"]:
        try:
            return ScoreboardMessage.parse(message)
        except AssertionError:  # I'm tooo lazy to make own exception and idk how to check and throw in one line
            return None
