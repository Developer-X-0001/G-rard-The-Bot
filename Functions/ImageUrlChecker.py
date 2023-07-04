import imghdr
import urllib.request

def is_image_url(url: str):
    try:
        with urllib.request.urlopen(url) as response:
            image_data = response.read()
            return imghdr.what(None, image_data) is not None
    except:
        return False