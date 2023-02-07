import cv2 as cv
from dotenv import load_dotenv
import sys, requests, os

load_dotenv()

MAC = os.getenv("MAC")
API_TOKEN = os.getenv("API_TOKEN")
CLIENT_URL = os.getenv("CLIENT_URL")
FLOOR_URL = os.getenv("FLOOR_URL")
IMAGE_URL = os.getenv("IMAGE_URL")
DOT_SIZE = int(os.getenv("DOT_SIZE"))

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"{API_TOKEN}",
}


def get_client_floor_id(mac):
    url = CLIENT_URL + mac
    headers = HEADERS
    
    response = requests.request("GET", url, headers=headers).json()
   
    floorId = response["results"][0]["floorId"]
    client_x = round(response["results"][0]["coordinates"][0])
    client_y = round(response["results"][0]["coordinates"][1])

    return floorId, client_x, client_y


def get_floor_image_filename(floorId):
    url = FLOOR_URL + floorId
    headers = HEADERS
    
    response = requests.request("GET", url, headers=headers).json()
    
    image_filename = response["map"]["details"]["image"]["imageName"]
    image_width = round(response["map"]["details"]["width"])
    image_length = round(response["map"]["details"]["length"])
    image_detail_width = round(response["map"]["details"]["image"]["width"])
    
    return image_filename, image_width, image_length, image_detail_width


def get_floor_image(image):
    url = IMAGE_URL + image
    headers = HEADERS
    
    response = requests.request("GET", url, headers=headers)
    
    file = open(image, "wb")  ## Creates the file for image
    file.write(response.content)  ## Saves file content
    file.close()


def draw_client_location(image, mac, x, y, width, length, detail_width):
    img = cv.imread(image, 3)
    if img is None:
        sys.exit("Could not read the image.")
    red = [0, 0, 255]
    conversion = detail_width/width
    x = round(x * conversion)
    y = round(y * conversion)
    img = cv.circle(img, (x, y), DOT_SIZE, red, -1)
    cv.imwrite(f"location_client_{mac}.jpg", img)
    os.remove(image)

def main():
    try:
        # Get the current floor where the client is active
        client_floor_id, x, y = get_client_floor_id(MAC)
        # Get the floor image filename
        (
            floor_image_filename,
            floor_image_width,
            floor_image_length,
            floor_image_detail_width,
        ) = get_floor_image_filename(client_floor_id)
        # Get the actual image
        floor_image = get_floor_image(floor_image_filename)
        # Draw location of client op image
        draw_client_location(
            floor_image_filename, MAC, x, y, floor_image_width, floor_image_length, floor_image_detail_width
        )
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()