import base64
from PIL import Image


def img_to_base64(img: Image) -> str:
    """ Converts an image to a base64 string. """

    return base64.b64encode(img.tobytes()).decode('utf-8')