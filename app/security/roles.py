from enum import Enum


class Role(str, Enum):
    OPERATOR = "OPERATOR"       # read-only
    SUPERVISOR = "SUPERVISOR"   # approvals only
    AUDITOR = "AUDITOR"         # read-only
