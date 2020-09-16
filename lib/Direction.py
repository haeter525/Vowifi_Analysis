import enum

class Direction(enum.Enum):
    UPWARD = -1
    DOWNWARD = 1

DIRECTION_NAMES = [ x.name for x in Direction ]