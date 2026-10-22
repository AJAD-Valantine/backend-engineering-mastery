from enum import Enum


class CopyStatus(str, Enum):
    ACTIVE = "active"
    LOANED = "loaned"
    DAMAGED = "damaged"
    RETIRED = "retired"
    LOST = "lost"
