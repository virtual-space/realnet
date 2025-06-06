import os
from dotenv import *

path = os.path.join(os.getcwd(), ".env")
if os.path.exists(path):
    load_dotenv(dotenv_path=path)

def load_config():
    """Load configuration from environment variables."""
    return Config()

class Config:

    def get_database_url(self):
        db_type = os.getenv('REALNET_DB_TYPE', 'postgresql')
        if db_type == 'sqlite':
            db_name = os.getenv('REALNET_DB_NAME', 'realnet')
            return f'{db_type}:///{db_name}.db'
        else:
            db_user = os.getenv('REALNET_DB_USER', 'realnet')
            db_pass = os.getenv('REALNET_DB_PASS', 'realnet')
            db_host = os.getenv('REALNET_DB_HOST', 'localhost')
            db_port = os.getenv('REALNET_DB_PORT', '5432')
            db_name = os.getenv('REALNET_DB_NAME', 'realnet')
            return f'{db_type}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

    def get_db_type(self):
        return os.getenv('REALNET_DB_TYPE')

    def get_server_host(self):
        return os.getenv('REALNET_SERVER_HOST')

    def get_server_port(self):
        return os.getenv('REALNET_SERVER_PORT')

    def get_storage_type(self):
        return os.getenv('REALNET_STORAGE_TYPE')

    def get_storage_path(self):
        return os.getenv('REALNET_STORAGE_PATH')

    def get_s3_region(self):
        return os.getenv('REALNET_STORAGE_S3_REGION')

    def get_s3_bucket(self):
        return os.getenv('REALNET_STORAGE_S3_BUCKET')

    def get_s3_key(self):
        return os.getenv('REALNET_STORAGE_S3_KEY')

    def get_s3_secret(self):
        return os.getenv('REALNET_STORAGE_S3_SECRET')

    def get_app_secret(self):
        return os.getenv('REALNET_APP_SECRET')

    def get_jwt_key(self):
        return os.getenv('REALNET_JWT_KEY')

    def get_jwt_issuer(self):
        return os.getenv('REALNET_JWT_ISSUER')

    def get_base64_encode_data(self):
        return os.getenv('REALNET_BASE64_ENCODE_DATA', False)

    def get_sqs_url(self):
        return os.getenv('REALNET_SQS_URL')

    def get_use_s3_upload_url(self):
        return os.getenv('REALNET_USE_S3_UPLOAD_URL', False)
