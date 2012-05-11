import os
from findi import FindMyIPhone

# be careful storing your personal apple id in files. In this case we make it an environment variable

APPLE_EMAIL = os.environ.get("APPLE_EMAIL")
APPLE_PASSWORD = os.environ.get("APPLE_PASSWORD")

# initialize findmyiphone with your apple ID

iphone = FindMyIPhone(APPLE_EMAIL, APPLE_PASSWORD)

# locate the iphone

iphone_location = iphone.locate()

# iphone.locate() returns a dictionary that contains a latitude and longitude

latitude = iphone_location.get('latitude')
longitude = iphone_location.get('longitude')
