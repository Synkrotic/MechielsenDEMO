import sys
import config
import network
from time import sleep

connection = network.WLAN(network.STA_IF)

def check_connection():
    return connection.isconnected()


def connect():

    if connection.isconnected():
        print("Already connected")
        print(connection.config('essid'))
        return True

    connection.active(True)
    print(config.WIFI_SSID, config.WIFI_PASSWORD)
    connection.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    retry = 0
    while not connection.isconnected():  # wait until connection is complete
        if retry == 10:  # try 10 times
            print("beans")
            # return False
            sys.exit("Could not establish connection, check your settings")
        retry += 1

        sleep(1)  # check again in a sec

    # no exit, we have a connection!
    print("Connection established")
    return True


# while not check_connection():
connect()