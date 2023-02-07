# Locate Client

This tool can locate a client based on its MAC adres. The location is drawn on the floor image where the client is located

## Description

This tool makes us of the DNA Spaces API to retrieve a client floor location and uses this floor location
to retrieve the floor image and draws a circle at the client location. This image is then saved as "location_client_MACADDRESS.jpg"

## Getting Started

### Installing

* Rename .env_EXMPLE to .env and fill out the .env file
* Create a virtual environment and activate it
* Run pip install -r requirements.txt

### Executing program

```
locate_client.py
```

