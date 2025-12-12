from enum import Enum, auto

class MessageType(Enum):
    MODEL_UPDATE = auto()
    MASK = auto()
    AGGREGATION_RESULT = auto()
    CONTROL = auto()
    HEARTBEAT = auto()
