import boto3
import json
from functools import lru_cache
from config.settings import settings

secrets_client = boto3.client("secretsmanager", region_name=settings.AWS_REGION)

@lru_cache()
def get_secret(secret_name: str) -> dict:
    response = secrets_client.get_secret_value(SecretId=secret_name)
    return json.loads(response["SecretString"])

def get_api_keys() -> dict:
    return get_secret("customer-support/api-keys")

def get_db_credentials() -> dict:
    return get_secret("customer-support/db-credentials")