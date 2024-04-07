import os
from dotenv import load_dotenv


class Config:
    prod: bool

    app_name: str
    bucket_name: str
    covers_bucket_name: str

    file_prefix: str

    s3_endpoint: str
    s3_key_id: str
    s3_access_key: str

    def __init__(self):
        self.prod = os.environ.get('PRODUCTION', 'false') == 'true'

        self.app_name = os.environ.get('APP_NAME', 'Anime.News')
        self.bucket_name = os.environ.get('BUCKET_NAME', 'previews')
        self.covers_bucket_name = os.environ.get('COVERS_BUCKET_NAME', 'covers')
        self.file_prefix = os.environ.get('FILE_PREFIX', 'output')

        self.s3_endpoint = os.environ.get('S3_ENDPOINT')
        self.s3_key_id = os.environ.get('S3_KEY_ID')
        self.s3_access_key = os.environ.get('S3_ACCESS_KEY')


def get_config() -> Config:
    load_dotenv()

    return Config()
