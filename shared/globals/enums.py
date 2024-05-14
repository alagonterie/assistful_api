from enum import Enum

from shared.globals.constants import FIELD_ORG_ID


class AccessLevels(Enum):
    SERVICE = 0
    ADMIN = 1
    ADMIN_OWNER = 2
    OWNER = 3


class CustomClaimKeys(Enum):
    ACCESS_LEVEL = 'access_level'
    ORG_ID = FIELD_ORG_ID


class ChatbotTemperaments(Enum):
    TAME = 1
    FUN = 2
    LOOSE = 3
    WILD = 4
