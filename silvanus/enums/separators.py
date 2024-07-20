

from enum import Enum


class Separators(str, Enum):
    OPEN_CHAR = "{"
    CLOSE_CHAR = "}"
    DELIMITER = "/"

    QUERY_AND = "&"
    QUERY_EQUAL = "="
