import glob
import os

from django.conf import settings
from minio import Minio

MEDIA_PATH = settings.MEDIA_ROOT

client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)


def get_media_files() -> list[str]:
    return [
        local_file
        for local_file in glob.glob(MEDIA_PATH + "/**", recursive=True)
        if os.path.isfile(local_file)
    ]


def get_remote_paths(media_file):
    return media_file[len(MEDIA_PATH) :].replace(os.sep, "/")


def upload_file(media_file):
    client.fput_object(
        settings.MINIO_MEDIA_FILES_BUCKET,
        get_remote_paths(media_file),
        media_file,
    )


media_files = get_media_files()
for mf in media_files:
    upload_file(mf)
