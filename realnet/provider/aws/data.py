from realnet.core.config import Config
from realnet.core.provider import DataProvider
from realnet.core.type import Data

import boto3

cfg = Config()

class S3DataProvider(DataProvider):
    
    def __init__(self, bucket_name = cfg.get_s3_bucket()):
        self.bucket_name = bucket_name
        self.session = boto3.Session(
            aws_access_key_id=cfg.get_s3_key(),
            aws_secret_access_key=cfg.get_s3_secret(),
            region_name=cfg.get_s3_region()
        )

    def get_data(self, id):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        s3_obj = bucket.Object(id).get()
        if s3_obj:
            return Data(id, s3_obj['ContentType'], s3_obj['ContentLength'], s3_obj['Body'].read())
        else:
            return None

    def update_data(self, id, storage):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.Object(id).put(Body=storage)

    def delete_data(self, id):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.Object(id).delete()