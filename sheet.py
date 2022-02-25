from typing import List, Optional, Tuple, Any

from functions import bool_or_else, find, list_expand, int_or_else


HEADER_ROW_INDEX = 0

ORDER_NUMBER_COLUMN_INDEX = 0
REAL_NAME_COLUMN_INDEX = 1
REPOS_COLUMN_INDEX = 3
YOUTUBE_NAME_COLUMN_INDEX = 3
TIME_CODES_COLUMN_INDEX = 4
TOTAL_SCORES_COLUMN_INDEX = 5


EMPTY_CELL = ""


def is_cell_empty(data) -> bool:
    return type(data) == str and not data.strip()


class Sheet(object):

    def __init__(self, document_id: str, cells: str, data: dict, url: Optional[str] = None):
        self.document_id = document_id
        self.data = data
        self.cells = cells
        self.url = url

        data["range"] = cells

        self.values: List[List] = data["values"]

        self.headers = self.values[HEADER_ROW_INDEX]
        self.rows = [it for it in self.values[HEADER_ROW_INDEX + 1:]
                     if not is_cell_empty(it[ORDER_NUMBER_COLUMN_INDEX])]

    def fix_flags(self, columns: List[int]):
        """
        Function convert item type to bool from rows if possible for given index_column_names of header
        """
        for row in self.rows:
            for index in filter(lambda it: len(row) > it, columns):
                # convert to bool or leave as is, fuck u google
                row[index] = bool_or_else(row[index], row[index])

    def student_or_none(self, name: str) -> Optional[List[str]]:
        return find(lambda it: it[REAL_NAME_COLUMN_INDEX] == name, self.rows)

    def get_header_index(self, header: Any):
        try:
            return self.headers.index(header)
        except ValueError:
            return -1

    def get_clean_header_indexes(self, headers: List) -> List[int]:
        return [self.get_header_index(it) for it in headers if self.is_header_exists(it)]

    def is_header_exists(self, header: Any):
        return self.get_header_index(header) != -1

    def add_score(self, name: str, header: Any, score: int = 1):
        index = self.get_header_index(header)
        assert index != -1, f"Can't find date column '{header}' in table headers"
        student = self.student_or_none(name)

        if student is not None:
            list_expand(student, EMPTY_CELL, index + 1)
            old_score = student[index] if not is_cell_empty(student[index]) else 0
            new_score = old_score + score
            student[index] = str(new_score)
            return new_score

        return None

    def get_timecoders(self) -> List[str]:
        return [row[REAL_NAME_COLUMN_INDEX] for row in self.rows if row[TIME_CODES_COLUMN_INDEX]]
