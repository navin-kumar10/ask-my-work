from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.config import settings


class QdrantStore:
    def __init__(self):
        self.client = QdrantClient(url=settings.qdrant_url)

    def ensure(self, size: int):
        names = [collection.name for collection in self.client.get_collections().collections]
        if settings.qdrant_collection not in names:
            self.client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=size, distance=Distance.COSINE),
            )

    def upsert(self, items: list[dict]):
        self.client.upsert(
            collection_name=settings.qdrant_collection,
            points=[
                PointStruct(id=item["id"], vector=item["vector"], payload=item["payload"])
                for item in items
            ],
        )

    def search(self, vector: list[float], limit: int = 5):
        return self.client.query_points(
            collection_name=settings.qdrant_collection,
            query=vector,
            limit=limit,
            with_payload=True,
        ).points
