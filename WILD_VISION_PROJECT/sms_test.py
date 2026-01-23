from twilio.rest import Client
import os

# Use environment variables for credentials
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")

FROM_NUMBER = os.getenv("TWILIO_PHONE_FROM", "+1234567890")
TO_NUMBER   = os.getenv("TWILIO_PHONE_TO", "+1234567890")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

message = client.messages.create(
    body="✅ Wild Vision SMS test successful",
    from_=FROM_NUMBER,
    to=TO_NUMBER
)

print("SMS SID:", message.sid)
