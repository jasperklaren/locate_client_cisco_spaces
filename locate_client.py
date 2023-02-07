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
    "Authorization": f"Bearer {API_TOKEN}",
}


def get_client_floor_id(mac):
    url = CLIENT_URL + mac
    headers = HEADERS

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 401:
        raise Exception(
            f"Failed to get response from Cisco Spaces (code: {response.status_code}) API token invalid"
        )

    response = response.json()
    if not response["results"]:
        raise Exception(
            f"No client found. Is it a wireless client? or check MAC ({MAC})"
        )
    else:
        floorId = response["results"][0]["floorId"]
        client_x = round(response["results"][0]["coordinates"][0])
        client_y = round(response["results"][0]["coordinates"][1])
        client_last_seen = response["results"][0]["lastLocatedAt"]
        client_username = response["results"][0]["userName"]
        client_ip = response["results"][0]["ipAddress"]
        client_associated_ap = response["results"][0]["associatedApName"]
        client_associated = response["results"][0]["associated"]

        return (
            floorId,
            client_x,
            client_y,
            client_last_seen,
            client_username,
            client_ip,
            client_associated_ap,
            client_associated,
        )


def get_floor_image_filename(floorId):
    url = FLOOR_URL + floorId
    headers = HEADERS

    response = requests.request("GET", url, headers=headers).json()

    image_filename = response["map"]["details"]["image"]["imageName"]
    image_width = round(response["map"]["details"]["width"])
    image_length = round(response["map"]["details"]["length"])
    image_detail_width = round(response["map"]["details"]["image"]["width"])
    floor_name = response["map"]["name"]

    return image_filename, image_width, image_length, image_detail_width, floor_name


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
        raise Exception(f"Could no read image file: {image}")
    red = [0, 0, 255]
    conversion = detail_width / width
    x = round(x * conversion)
    y = round(y * conversion)
    img = cv.circle(img, (x, y), DOT_SIZE, red, -1)
    save_as = f"location_client_{mac}.jpg"
    cv.imwrite(save_as, img)
    os.remove(image)
    
    return save_as


def main():
    try:
        # Get the current floor where the client is active and some extra metadata about the client
        (
            client_floor_id,
            x,
            y,
            last_seen,
            username,
            ip,
            associated_ap,
            associated,
        ) = get_client_floor_id(MAC)

        # Get the floor image filename and some extra metadata about the floor
        (
            floor_image_filename,
            floor_image_width,
            floor_image_length,
            floor_image_detail_width,
            floor_name,
        ) = get_floor_image_filename(client_floor_id)

        # Get the actual image and save to disk
        get_floor_image(floor_image_filename)

        # Draw location of client on the downloaded image
        file_name = draw_client_location(
            floor_image_filename,
            MAC,
            x,
            y,
            floor_image_width,
            floor_image_length,
            floor_image_detail_width,
        )

        # Print result information
        print(
            f""" 
        Image filename: {file_name}
        MAC: {MAC}
        Username: {username}
        IP: {ip}
        Floor: {floor_name}
        Is Associated: {associated}
        Associated Accesspoint: {associated_ap}
        Last Seen: {last_seen}
        """
        )
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
