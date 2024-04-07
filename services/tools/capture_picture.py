import base64

from django.core.files.base import ContentFile
from django.utils.timezone import datetime


def save_img(base64Img):
    format, imgstr = base64Img.split(";base64,")
    ext = format.split("/")[-1]
    name = f"img_{datetime.now()}.{ext}"
    data = ContentFile(base64.b64decode(imgstr), name=name)
    return data, name, ext
