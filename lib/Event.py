import enum

class Event(enum.Enum):
    NONE = 0
    INVITE1 = 1
    TRYING2 = 2
    SESSION3 = 3
    PRACK4 = 4
    OK5 = 5
    RINGING6 = 6
    PRACK7 = 7
    OK8 = 8
    OK9 = 9
    ACK10 = 10
    VOICE11 = 11
    BYE12 = 12
    OK13 = 13
    
EVENT_NAMES = [ x.name for x in Event ]

