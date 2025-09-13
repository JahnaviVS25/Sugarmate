import requests
from twilio.rest import Client
import logging
import schedule
import time

# Configuration
NIGHTSCOUT_URL = "https://siddhu-cgm.herokuapp.com/api/v1/entries.json?count=1"
CRITICAL_THRESHOLD = 70  # mg/dL
TWILIO_ACCOUNT_SID = "<YOUR_TWILIO_ACCOUNT_SID>"
TWILIO_AUTH_TOKEN = "<YOUR_TWILIO_AUTH_TOKEN>"
TWILIO_FROM_NUMBER = "<YOUR_TWILIO_PHONE_NUMBER>"
USER_PHONE_NUMBER = "<USER_MOBILE_NUMBER>"

# Setup logging
logging.basicConfig(filename="glucose_alerts.log", level=logging.INFO,
                    format="%(asctime)s %(levelname)s: %(message)s")

def fetch_latest_glucose():
    try:
        response = requests.get(NIGHTSCOUT_URL)
        response.raise_for_status()
        data = response.json()
        if data and isinstance(data, list):
            return data[0].get("sgv")
        return None
    except Exception as e:
        logging.error(f"Error fetching glucose data: {e}")
        return None

def place_call():
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            to=USER_PHONE_NUMBER,
            from_=TWILIO_FROM_NUMBER,
            twiml='<Response><Say>Alert! Your glucose level is critically low. Please take action immediately.</Say></Response>'
        )
        logging.info(f"Placed call: SID {call.sid}")
    except Exception as e:
        logging.error(f"Error placing call: {e}")

def check_glucose_and_alert():
    glucose = fetch_latest_glucose()
    if glucose is not None:
        logging.info(f"Latest glucose reading: {glucose} mg/dL")
        if glucose < CRITICAL_THRESHOLD:
            logging.warning(f"Critical glucose level detected: {glucose} mg/dL")
            place_call()
        else:
            logging.info("Glucose level is normal.")
    else:
            logging.error("Failed to retrieve glucose reading.")

def main():
    schedule.every(2).minutes.do(check_glucose_and_alert)
    logging.info("Started glucose monitoring system.")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
