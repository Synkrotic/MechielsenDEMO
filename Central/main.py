import asyncio
import bluetooth
import time
import aioble

MY_SERVICE_UUID = bluetooth.UUID("0000A000-0000-1000-8000-00805F9B34FB")
MY_CHARACTERISTIC_UUID = bluetooth.UUID("0000A001-0000-1000-8000-00805F9B34FB")
RECEIVE_SERVICE_UUID = bluetooth.UUID("0000A002-0000-1000-8000-00805F9B34FB")
RECEIVE_CHARACTERISTIC_UUID = bluetooth.UUID("0000A003-0000-1000-8000-00805F9B34FB")

CLUTCH_PICO_NAME = "PicoW_Clutch"
CENTRAL_PICO_NAME = "PicoW_Central"

connection_device = None
connection_clutch = None

# Peripheral Role - Start advertising so another device can connect
async def start_advertising():
    # Define service and characteristic
    service = aioble.Service(MY_SERVICE_UUID)
    char = aioble.Characteristic(service, MY_CHARACTERISTIC_UUID,
                                 read=True, write=True, notify=True)
    
    # Register the service and characteristic with aioble
    aioble.register_services(service)
    
    print("Advertising...")
    global connection_clutch
    # Pass the UUID of the service rather than the service object itself
    connection_clutch = await aioble.advertise(name=CENTRAL_PICO_NAME, services=[MY_SERVICE_UUID], interval_us=10_000)
    print("Device connected to me (peripheral):", connection_clutch.device)
    await connection_clutch.disconnected()

# Central Role - Scan and connect to another device
async def connect_to_device():
    print("Scanning...")
    while not connection_clutch:
        async with aioble.scan(duration_ms=10_000) as scanner:
            async for result in scanner:
                # Access the device name and address from the result.device
                device_name = result.name()  # Use 'name()' to get the advertised name
                device_addr = result.device.addr  # Use 'device.addr' to get the device address
                if device_name:
                    print("Found device:", device_name, device_addr)

                if device_name == CLUTCH_PICO_NAME:
                    # Correctly initiate the connection using 'result.device.connect()'
                    global connection
                    connection = await result.device.connect()
                    print("Connected to device (central):", connection.device)
                    await connection.disconnected()
                    break

async def run():
    try:
        await connect_to_device()
        if connection_device:
            print("Connected to device (central):", connection_device.device)
        if connection_clutch:
            print("Connected to device (peripheral):", connection_clutch.device)

    except KeyboardInterrupt:
        print("Stopping...")


# Run both roles concurrently
async def main():
    await asyncio.gather(
        start_advertising(),
        run()
    )

asyncio.run(main())
