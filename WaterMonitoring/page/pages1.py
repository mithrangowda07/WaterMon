import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
import pytz
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_auth_token')    

client = Client(account_sid, auth_token)

# Twilio phone numbers
twilio_number = os.getenv('TWILIO_NUMBER')
receiver_number = os.getenv('RECEIVER_NUMBER')

# ThingSpeak settings
THINGSPEAK_READ_URL = os.getenv('THINGSPEAK_READ_URL')
THINGSPEAK_API_KEY = os.getenv('THINGSPEAK_API_KEY')

# Email settings
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')  # Replace with your email
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Replace with your email password
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')  # Replace with the recipient's email

# Global variables
flag = 0
threshold = 5
last_reset_date = None

# Timezone for date and time
LOCAL_TIMEZONE = pytz.timezone('Asia/Kolkata')


def reset_flag_if_needed():
    """
    Resets the global flag to 0 if the day has changed.
    """
    global flag, last_reset_date
    current_date = datetime.now(LOCAL_TIMEZONE).date()

    if last_reset_date is None or last_reset_date != current_date:
        flag = 0  # Reset the flag
        last_reset_date = current_date


def convert_to_local_time(utc_timestamp):
    """
    Converts a UTC timestamp string to local time in the specified timezone.
    """
    try:
        utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%SZ")
        local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(LOCAL_TIMEZONE)
        return local_time
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return None


def send_sms_alert(message_body):
    """
    Sends an SMS alert using Twilio.
    """
    try:
        message = client.messages.create(
            body=message_body,
            from_=twilio_number,
            to=receiver_number
        )
        print(f"SMS sent: {message.body}")
    except Exception as e:
        print(f"Error sending SMS: {e}")


def send_email_alert(subject, body):
    """
    Sends an email alert using SMTP.
    """
    try:
        # Set up the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        # Add the email body
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Upgrade the connection to secure
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Login to the email account
            server.send_message(msg)  # Send the email
            print(f"Email sent to {EMAIL_RECEIVER}: {subject}")
    except Exception as e:
        print(f"Error sending email: {e}")


def fetch_data():
    """
    Fetches data from ThingSpeak and sends alerts based on threshold conditions.
    """
    global flag

    try:
        # Fetch data from ThingSpeak
        response = requests.get(THINGSPEAK_READ_URL, params={'api_key': THINGSPEAK_API_KEY, 'results': 100})

        if response.status_code == 200:
            data = response.json()
            last_feed = data['feeds'][-1]
            last_timestamp = last_feed.get('created_at')
            last_value = last_feed.get('field2')

            # Convert timestamp to local time and validate date
            local_time = convert_to_local_time(last_timestamp)
            if local_time and local_time.date() != datetime.now(LOCAL_TIMEZONE).date():
                last_value = 0  # Ignore old data

            # Ensure last_value is valid and numeric
            if last_value is not None:
                last_value = float(last_value)

                reset_flag_if_needed()

                # Check thresholds and send alerts
                if last_value > threshold and flag == 0:
                    flag = 1
                    alert_message = f"Alert! The threshold level of 5 Litres has been exceeded. Current usage: {last_value:.2f} Litres."
                    send_sms_alert(alert_message)
                    send_email_alert("Threshold Exceeded Alert", alert_message)

                if last_value > 2 * threshold and flag == 1:
                    flag = 2
                    alert_message = f"Urgent Alert! Double the threshold level (10 Litres) has been used. Current usage: {last_value:.2f} Litres."
                    send_sms_alert(alert_message)
                    send_email_alert("Double Threshold Exceeded Alert", alert_message)

                return [last_value, flag]

            else:
                print("Error: Invalid data received from ThingSpeak.")
        else:
            print(f"Error: ThingSpeak API responded with status code {response.status_code}.")
    except Exception as e:
        print(f"Error fetching data from ThingSpeak: {e}")

    return -1

def calculate_charges(total_usage_liters):
    data = {
        'Domestic': ['0 to 8000 Litres', '8001 to 25000 Litres', '25001 to 50000 Litres', 'Above 50000 Litres'],
        'Rate': [7.00, 11.00, 26.00, 45.00],  # Rates in Rs. per KL
    }
    """Calculate the water charges based on the slab system."""
    total_usage_kl = total_usage_liters / 1000  # Convert liters to kiloliters (KL)
    charges = 0

    if total_usage_kl <= 8:  # Up to 8000 Liters (8 KL)
        charges = total_usage_kl * data['Rate'][0]
    elif total_usage_kl <= 25:  # Between 8001 and 25000 Liters
        charges = 8 * data['Rate'][0]  # Fixed charge for first 8 KL
        charges += (total_usage_kl - 8) * data['Rate'][1]
    elif total_usage_kl <= 50:  # Between 25001 and 50000 Liters
        charges = 8 * data['Rate'][0]  # Fixed charge for first 8 KL
        charges += 17 * data['Rate'][1]  # Fixed charge for next 17 KL
        charges += (total_usage_kl - 25) * data['Rate'][2]
    else:  # Above 50000 Liters
        charges = 8 * data['Rate'][0]  # Fixed charge for first 8 KL
        charges += 17 * data['Rate'][1]  # Fixed charge for next 17 KL
        charges += 25 * data['Rate'][2]  # Fixed charge for next 25 KL
        charges += (total_usage_kl - 50) * data['Rate'][3]

    charges = charges + 56
        
    return charges