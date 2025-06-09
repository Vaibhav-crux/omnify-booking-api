from enum import Enum

class RecordStatus(str, Enum):
    active = "active"
    inactive = "inactive"
    cancelled = "cancelled"
    revoked = "revoked"

class UserStatus(str, Enum):
    active = "active"
    banned = "banned"
    suspended = "suspended"
