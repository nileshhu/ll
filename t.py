import requests

bot_token = "5866208034:AAE9685WjS-3Cx48fahACoXLCLT0dj7Ro6Y"
chat_id = "5227929164"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)
    return response.json()

test_message = "This is a test message from the SMS Forwarder script."
send_to_telegram(test_message)
