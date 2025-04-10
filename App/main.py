import asyncio
from bleak import BleakScanner, BleakClient
from ui import Ui
import threading

PICO_NAME = "PicoW_Central"
CHARACTERISTIC_UUID = "0000A001-0000-1000-8000-00805F9B34FB" # CENTRAL UUID: 0000A001-0000-1000-8000-00805F9B34FB | CLUTCH UUID: 0000A003-0000-1000-8000-00805F9B34FB
UI = Ui()

sender_address = None

async def connectToPico(pico_address):
    if pico_address is not None:
        try:
            async with BleakClient(pico_address) as client:
                global sender_address
                sender_address = pico_address
                while client:
                    value = await client.read_gatt_char(CHARACTERISTIC_UUID)
                    try:
                        decoded_str = value.decode('utf-8')
                        await analyseData(decoded_str)
                    except Exception as e:
                        print("Error decoding bytearray:", e)
        except Exception as e:
            await disconnectFromPico()
            print("Error connecting to Pico:", e)


async def analyseData(data):
    if len(data) < 1: return

    # updated_data = data.replace("(", "").replace(")", "")
    # data_list = updated_data.split(", ")
    # clutch_id = data_list[0]
    # clutch_value = data_list[1]
    # UI.clutches[int(clutch_id)].updateLight(int(clutch_value))


    # print(f"Received data: {data}")
    updated_data = data.replace("[", '').replace("}]", '').replace("'", '"')
    clutches = updated_data.split("}, ")
    if len(clutches)  < 1: return
    for clutch in clutches:
        data = clutch.split(", ")
        clutch_id = data[0].split(": ")[1]
        clutch_value = data[1].split(": ")[1]
        UI.clutches[int(clutch_id)].updateLight(int(clutch_value))
        print(f"Clutch {clutch_id} value: {clutch_value}")


async def disconnectFromPico(pico_address=sender_address):
    if pico_address is not None:
        try:
            async with BleakClient(pico_address) as client:
                await client.disconnect()
        except Exception as e:
            print("Error disconnecting from Pico:", e)


async def run():
    while True:
        try:
            devices = await BleakScanner.discover()
            for device in devices:
                if device.name:
                    print("Found device:", device.name, device.address)
                    if device.name == PICO_NAME:
                        await connectToPico(device.address)
                        break
        except Exception as e:
            await disconnectFromPico()
            print("Error:", e)


threading.Thread(target=lambda: asyncio.run(run()), daemon=True).start()
UI.run()