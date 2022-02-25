from collections import Iterable, Callable, Generator
from datetime import datetime
from typing import Optional, List


def int_or_else(string: str, default: Optional[int] = None, base: int = 10) -> Optional[int]:
    try:
        return int(string, base)
    except ValueError:
        return default


def bool_or_else(string: str, default: Optional[bool] = None) -> Optional[bool]:
    lower = string.lower()
    if lower == "true":
        return True
    elif lower == "false":
        return False
    else:
        return default


def predicate_generator(predicate: Callable, iterable: Iterable) -> Generator:
    return (it for it in iterable if predicate(it))


def first(predicate: Callable, iterable: Iterable):
    return next(predicate_generator(predicate, iterable))


def first_not_none_or_none(function: Callable, iterable: Iterable):
    for it in iterable:
        value = function(it)
        if value is not None:
            return value
    return None


def find(predicate: Callable, iterable: Iterable):
    return next(predicate_generator(predicate, iterable), None)


def list_expand(lst: List, default, size: int):
    remain = size - len(lst)

    # nothing to do required
    if remain <= 0:
        return

    for _ in range(remain):
        lst.append(default)


DATE_FORMAT = "%d.%m.%Y"
EXCEL_START_DATE = datetime(1900, 1, 1)
EXCEL_DATE_OFFSET = 2


def strdate(date: datetime) -> str:
    return date.strftime(DATE_FORMAT)


def strdate_now():
    return strdate(datetime.now())


def date2excel(date: datetime) -> int:
    return date.toordinal() - EXCEL_START_DATE.toordinal() + EXCEL_DATE_OFFSET


def strdate2excel(string: str) -> int:
    date = datetime.strptime(string, DATE_FORMAT)
    return date2excel(date)


def from_base26(string: str) -> int:
    start, end = 'A', 'Z'
    total = ord(end) - ord(start) + 1
    letters = string.split()
    assert all(it >= start <= end for it in letters), f"Invalid letter in string to converter: {string}"
    return sum((ord(it) - ord(start)) * pow(total, index) for index, it in enumerate(letters))