import network
import socket
import json
from RFID import readRfid
from time import sleep

# Set up the Pico W as an Access Point (hotspot)
ap = network.WLAN(network.AP_IF)
ap.config(essid='PicoW-API', password='00000000')  # You can change the SSID and password
ap.active(True)

print('Starting access point...')
while not ap.active():
    sleep(1)
print('Access point active')
print('AP IP address:', ap.ifconfig()[0])

# Basic HTTP response headers
def http_response(client, status_code=200, content_type='application/json', body='{}'):
    response = f"HTTP/1.1 {status_code} OK\r\nContent-Type: {content_type}\r\n\r\n{body}"
    client.send(response)

# Start the web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
server = socket.socket()
server.bind(addr)
server.listen(1)

print("Listening for HTTP connections on", addr)

while True:
    try:
        client, client_addr = server.accept()
        print('Client connected from', client_addr)
        request = client.recv(1024)
        request_str = request.decode('utf-8')
        print('Request:', request_str)

        # Simple routing
        if 'GET /api/data' in request_str:
            data = [
                readRfid().getFormatted(),
                readRfid(1).getFormatted(),
                readRfid(2).getFormatted(),
                readRfid(3).getFormatted(),
                readRfid(4).getFormatted(),
                readRfid(5).getFormatted()
            ]
            body = json.dumps(data)
            http_response(client, body=body)
        else:
            http_response(client, status_code=404, body=json.dumps({"error": "Not Found"}))

        client.close()
    except KeyboardInterrupt:
        server.close()
        ap.active(False)
        print("Access point stopped")
        break
    except Exception as e:
        print("Error:", e)
