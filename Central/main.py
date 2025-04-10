import config
import urequests as requests

url = f"http://{config.SERVER}:{config.PORT}{config.ENDPOINT}"

while True:
    try:
        response = requests.get(url)
        answer = response.json()
        response.close()
        print(answer)
    except Exception as e:
        print(f"Error: {e}")
        break
        