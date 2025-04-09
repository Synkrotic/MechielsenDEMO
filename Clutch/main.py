import machine
import constants
import BLE_Device
import _thread
from constants import STATE_PAUSED
from mfrc522 import MFRC522



READER = MFRC522(spi_id=0, sck=6, miso=4, mosi=7, cs=5, rst=22)
BLE_DEVICE = None
CLUTCH_VALUE = 1129975462


class Data:
    def __init__(self, id: int, content):
        self.id = id
        self.content = content
        self.clutch_id = 0

    def __str__(self):
        return f'{{"id": {self.id}, "content": {self.content}}}'

    def getFormatted(self):
        status = -1
        if self.id == constants.SEND_TAG_DATA:
            status = 1 if self.content == CLUTCH_VALUE else 0
        return f'({self.clutch_id}, {status})'


State = constants.STATE_PLAYING
PollInterval = 200


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


def sendData(data: Data):
    print(data.getFormatted())


def getData() -> list[Data]:
    return []


InputHandlers = {
    constants.IN_SET_STATE: onSetState,
    constants.IN_SET_POLL_INTERVAL: onSetPollInterval
}

def run_device():
    global BLE_DEVICE
    BLE_DEVICE = BLE_Device.BLEDevice(name="PicoW_Clutch")
    BLE_DEVICE.run()
# 
# _thread.start_new_thread(run_device, ())
while True:
    for data in getData():
        InputHandlers[data.id](data)

    if State == STATE_PAUSED:
        continue

    readRfid()
    machine.lightsleep(PollInterval)