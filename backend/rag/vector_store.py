from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from config.settings import settings

def get_opensearch_client():
    credentials = boto3.Session().get_credentials()
    auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        settings.AWS_REGION,
        "aoss",
        session_token=credentials.token,
    )
    return OpenSearch(
        hosts=[{"host": settings.OPENSEARCH_ENDPOINT, "port": 443}],
        http_auth=auth,
        use_ssl=True,
        connection_class=RequestsHttpConnection,
    )


class VectorStore:
    def __init__(self):
        self.client = get_opensearch_client()
        self.index_name = "knowledge-base"

    def search(self, query_embedding: list[float], top_k: int = 3) -> list[dict]:
        body = {
            "size": top_k,
            "query": {
                "knn": {
                    "embedding": {
                        "vector": query_embedding,
                        "k": top_k
                    }
                }
            }
        }
        resp = self.client.search(index=self.index_name, body=body)
        return [hit["_source"] for hit in resp["hits"]["hits"]]

    def index_document(self, doc_id: str, content: str, embedding: list[float], metadata: dict):
        self.client.index(
            index=self.index_name,
            id=doc_id,
            body={
                "content": content,
                "embedding": embedding,
                "metadata": metadata,
            }
        )