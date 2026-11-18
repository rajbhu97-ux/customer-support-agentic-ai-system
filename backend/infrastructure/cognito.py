
import boto3
from config.settings import settings

cognito_client = boto3.client("cognito-idp", region_name=settings.REGION)

USER_POOL_ID = settings.COGNITO_USER_POOL_ID
CLIENT_ID = settings.COGNITO_CLIENT_ID