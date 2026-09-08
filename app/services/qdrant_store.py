from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings
import hashlib

class QdrantStore:
    def __init__(self): self.client = QdrantClient(url=settings.qdrant_url)
    def ensure(self, size=768):
        names=[c.name for c in self.client.get_collections().collections]
        if settings.qdrant_collection not in names:
            self.client.create_collection(settings.qdrant_collection, vectors_config=VectorParams(size=size, distance=Distance.COSINE))
    def upsert(self, items):
        self.client.upsert(settings.qdrant_collection, points=[PointStruct(id=hashlib.md5(i['id'].encode()).hexdigest(), vector=i['vector'], payload=i['payload']) for i in items])
    def search(self, vector, limit=5):
        return self.client.query_points(collection_name=settings.qdrant_collection, query=vector, limit=limit).points
