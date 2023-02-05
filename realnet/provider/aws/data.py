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
        try:
            s3_obj = bucket.Object(id)
            if s3_obj:
                s3_obj_data = s3_obj.get()
                return Data(id, s3_obj_data['ContentType'], s3_obj_data['ContentLength'], s3_obj_data['Body'].read())
            else:
                return None
        except:
            return None

    def update_data(self, id, storage):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.Object(id).put(Body=storage)

    def delete_data(self, id):
        s3 = self.session.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        bucket.Object(id).delete()

    def get_data_upload_url(self, id):
        s3 = self.session.client('s3')
        try:
            response = s3.generate_presigned_post(self.bucket_name,
                                                  id,
                                                  ExpiresIn=3600)
            return response
        except Exception as e:
            print(e)
            return None

    def confirm_data_upload(self, id):
        pass