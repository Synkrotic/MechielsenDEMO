import constants
from constants import STATE_PAUSED
from mfrc522 import MFRC522


READER = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
READERS =       [READER    , READER   , READER    , READER    , READER, READER]
CLUTCH_VALUES = [1129975462, 644487072, 3169280180, 1498623501, 0     , 0     ]


class Data:
    def __init__(self, id: int, value: int):
        self.clutch_id = id
        self.value = value

    def __str__(self):
        return f'{{"id": {self.clutch_id}, "value": {self.value}}}'

    def getFormatted(self):
        return {'i':self.clutch_id,'v':self.value}


State = constants.STATE_PLAYING
PollInterval = 200


def onSetState(data: Data):
    global State
    State = data.value


def onSetPollInterval(data: Data):
    global PollInterval
    PollInterval = data.value


def readRfid(index: int = 0) -> Data:
    READERS[index].init()
    (stat, tag_type) = READERS[index].request(READERS[index].REQIDL)
    if stat == READERS[index].OK:
        (stat, uid) = READERS[index].SelectTagSN()
        if stat == READERS[index].OK:
            card = int.from_bytes(bytes(uid), "little", False)
            print(f"Card {index}: {card}")
            return Data(index, 1 if card == CLUTCH_VALUES[index] else 0)
        else:
            return Data(index, -1)
    else:
        return Data(index, -1)


def sendData(data: Data):
    print(data.getFormatted())


# def getData() -> list[Data]:
#     return []


# InputHandlers = {
#     constants.IN_SET_STATE: onSetState,
#     constants.IN_SET_POLL_INTERVAL: onSetPollInterval
# }

# while True:
#     try:
#         for data in getData():
#             InputHandlers[data.id](data)

#         if State == STATE_PAUSED:
#             continue

#         readRfid()
#         machine.lightsleep(PollInterval)
#     except KeyboardInterrupt:
#         print("Finished.")
#         break