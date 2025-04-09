import machine

import constants
from constants import STATE_PAUSED
from mfrc522 import MFRC522
READER = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)

class Data:
    def __init__(self, id: int, content):
        self.id = id
        self.content = content


State = STATE_PAUSED
PollInterval = 500

def onSetState(data: Data):
    global State
    State = data.content


def onSetPollInterval(data: Data):
    global PollInterval
    PollInterval = data.content

def readRfid():
    READER.init()
    (stat, tag_type) = READER.request(READER.REQIDL)
    if stat == READER.OK:
        (stat, uid) = READER.SelectTagSN()
        if stat == READER.OK:
            card = int.from_bytes(bytes(uid), "little", False)
            sendData(Data(constants.SEND_TAG_DATA, card))
        else:
            sendData(Data(constants.SEND_ERROR_DATA, {'id': constants.ERROR_READER_NOT_OK, 'code': stat}))
    else:
        sendData(Data(constants.SEND_ERROR_DATA, {'id': constants.ERROR_NO_TAG, 'code': stat}))

InputHandlers = {
    constants.IN_SET_STATE: onSetState,
    constants.IN_SET_POLL_INTERVAL: onSetPollInterval
}

def sendData(data: Data):
    print(data)

def getData() -> list[Data]:
    return []


while True:
    for data in getData():
        InputHandlers[data.id](data)

    if State == STATE_PAUSED:
        continue

    readRfid()
    machine.lightsleep(PollInterval)