import boto3
import json
from config.settings import settings

bedrock_runtime = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)

def get_embedding(text: str) -> list[float]:
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text})
    )
    result = json.loads(response["body"].read())
    return result["embedding"]