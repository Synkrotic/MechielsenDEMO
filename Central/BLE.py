import bluetooth
import time
import aioble
import uasyncio as asyncio
from machine import Pin
from micropython import const

# BLE Constants
_IRQ_CENTRAL_CONNECT = const(1)  # Event for when a central device connects
_IRQ_CENTRAL_DISCONNECT = const(2)  # Event for when a central device disconnects
_IRQ_SCAN_RESULT = const(5)  # Event for scan result
_IRQ_GATTC_NOTIFY = const(18)

_FLAG_READ = const(0x02)  # Flag to indicate that the characteristic can be read
_FLAG_WRITE = const(0x08)  # Flag to indicate that the characteristic can be written
_FLAG_NOTIFY = const(0x10)  # Flag to indicate that the characteristic can notify

# Use proper 128-bit UUIDs for BLE compatibility
SERVICE_UUID = bluetooth.UUID("0000A000-0000-1000-8000-00805F9B34FB")  # UUID for the service
CHARACTERISTIC_UUID = bluetooth.UUID("0000A001-0000-1000-8000-00805F9B34FB")  # UUID for the characteristic
RECEIVE_SERVICE_UUID = bluetooth.UUID("0000A002-0000-1000-8000-00805F9B34FB")  # UUID for the service
RECEIVE_CHARACTERISTIC_UUID = bluetooth.UUID("0000A003-0000-1000-8000-00805F9B34FB")  # UUID for the characteristic

PICO_NAME = "PicoW_Central"  # Name of the Pico W device
CLUTCH_PICO_NAME = "PicoW_Clutch"  # Name of the Pico W device to connect to


clutches = [
    {
      "id": 0,
      "value": -1,
    },
    {
      "id": 1,
      "value": -1,
    },
    {
      "id": 2,
      "value": -1,
    },
    {
      "id": 3,
      "value": -1,
    },
    {
      "id": 4,
      "value": -1,
    },
    {
      "id": 5,
      "value": -1,
    }
]

class BLEDevice:
    def __init__(self, name="PicoW_Bluetooth"):
        self.name = name
        self.connected = False
        self.receiving = False
        self.conn_handle = None
        self.ble = bluetooth.BLE()  # Initialize the BLE object
        self.ble.active(True)  # Activate BLE
        self.ble.irq(self.ble_irq)  # Set the IRQ handler for BLE events
        self.pin = Pin("LED", Pin.OUT)  # Initialize the pin for the LED
        
        self.found_devices = []

        # Define GATT service with correct structure
        self.service = (
            SERVICE_UUID,
            ((CHARACTERISTIC_UUID, _FLAG_READ | _FLAG_NOTIFY | _FLAG_WRITE),),
        )

        # Register the service
        ((self.characteristic_handle,),) = self.ble.gatts_register_services((self.service,))
        
        self.start_advertising()
  
    def start_advertising(self, interval=100):
        """Start advertising BLE service"""
        print("Starting advertising...")
        payload = self.create_advertising_payload()
        self.ble.gap_advertise(interval, payload)

    def create_advertising_payload(self):
        """Create a proper advertising packet"""
        payload = bytearray()
        payload.extend(bytes([len(self.name) + 1, 0x09]))  # Length and type for Complete Local Name
        payload.extend(self.name.encode('utf-8'))
        return payload
    
    def update_clutches(self, data):
        """Update clutches based on received data"""
        try:
            updated_data = data.replace("(", "").replace(")", "")
            data_list = updated_data.split(", ")
            clutch_id = data_list[0]
            clutch_value = data_list[1]
            print(f"Updating clutch {clutch_id} to value {clutch_value}")
            for clutch in clutches:
                if clutch["id"] == int(clutch_id):
                    clutch["value"] = int(clutch_value)
                    print(f"Clutch {clutch_id} updated to {clutch_value}")
                    break
            else:
                print(f"Clutch ID {clutch_id} not found")
        except Exception as e:
            print(f"Error updating clutches: {e}")

    # def receive_payload(self):
    #     """Receive payload from the connected device"""
    #     print("Receiving payload...")
    #     if self.conn_handle is not None:
    #         try:
    #             print(f"Connection handle: {self.conn_handle}")
    #             data = self.ble.gatts_read(self.characteristic_handle)  # Read the characteristic value
    #             if data:
    #                 print(f"Received Payload: {data}")
    #                 # Process the received data (e.g., update clutches)
    #                 self.update_clutches(data)
    #         except OSError as e:
    #             print(f"Error receiving payload: {e}")

    def send_payload(self, payload_value=None):
        """Send payload to the connected device"""
        if payload_value is None:
            return
        payload = bytearray(str(payload_value), 'utf-8')
        # print(f"Sending payload: {payload} to handle: {self.characteristic_handle}")
        try:
            if self.conn_handle is not None and self.characteristic_handle is not None:
                self.ble.gatts_write(self.characteristic_handle, payload)  # Write the payload to the characteristic
                self.ble.gatts_notify(self.conn_handle, self.characteristic_handle, payload)  # type: ignore
                print(f"Sent Payload!")
            else:
                print("Connection handle or characteristic handle is None")
        except OSError as e:
            print(f"Error sending payload: {e}")

    def on_connect(self, conn_handle, addr_type, addr):
        """Handle BLE connection"""
        print(f"Connected to {addr}")
        self.conn_handle = conn_handle  # Store connection handle
        print(f"Connection handle: {self.conn_handle}")
        self.connected = True
        
    def on_disconnect(self, conn_handle, reason):
        """Handle BLE disconnection"""
        print(f"Disconnected. Reason: {reason} {conn_handle}")
        self.connected = False
        self.conn_handle = None  # Clear connection handle
        self.start_advertising()

    def ble_irq(self, event, data):
        """Handle BLE events"""
        # print(f"BLE IRQ event: {event}, data: {data}")
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, addr_type, addr = data
            self.on_connect(conn_handle, addr_type, addr)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            print("Disconnected")
            conn_handle, reason = data
            self.on_disconnect(conn_handle, reason)
        elif event == _IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            name = self.decode_name(bytearray(adv_data))
            if name == CLUTCH_PICO_NAME:
                print(f"Found {name} with address {addr}")
                self.connect_to_device(addr_type, addr)  # Connect to the device
        elif event == _IRQ_GATTC_NOTIFY:
            conn_handle, value_handle, data = data
            self.update_clutches(str(data, 'utf-8'))

    def decode_name(self, adv_data):
        i = 0
        while i < len(adv_data):
            length = adv_data[i]
            if length == 0:
                break
            field_type = adv_data[i + 1]
            if field_type == 0x09:  # Complete Local Name
                return adv_data[i + 2:i + 1 + length].decode('utf-8')
            elif field_type == 0x08:  # Shortened Local Name
                return adv_data[i + 2:i + 1 + length].decode('utf-8')
            elif field_type == 0x00:
                return 
            i += 1 + length
        return None

    def connect_to_device(self, addr_type, addr):
        """Connect to a BLE device"""
        print(f"Connecting to {addr}")
        try:
            self.ble.gap_connect(addr_type, addr)
        except Exception as e:
            print(f"Error connecting to device: {e}")
            return
        self.receiving = True

    def run(self):
        print("Advertising started. Look for 'PicoW_Bluetooth' on your phone.")
        print("LED starts flashing...")
        try:
            while True:
                if self.connected:
                    if not self.receiving:
                        self.ble.gap_scan(5000, 1000)
                    self.send_payload(clutches)
                    self.pin.on()
                    time.sleep(1)
                    
                if not self.connected:
                    self.pin.toggle()
                    time.sleep(1)
        except KeyboardInterrupt:
            self.pin.off()
            print("Finished.")

ble_device = BLEDevice(name=PICO_NAME)
ble_device.run()