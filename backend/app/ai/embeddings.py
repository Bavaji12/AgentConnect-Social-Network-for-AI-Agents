import math
import re
import hashlib
from typing import List
import numpy as np
from app.core.config import settings
from app.ai.base import BaseEmbeddingProvider

class DeterministicSemanticEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic domain-aware semantic embedding generator.
    Maps input text into a 384-dimensional unit vector using semantic concept clusters
    and feature hashing. Guarantees deterministic, reproducible, cosine-comparable embeddings
    without requiring external network calls or heavy weights.
    """
    def __init__(self, dim: int = 384):
        self.dim = dim
        # Semantic domain centroids defined in seed space
        self.domains = {
            "commerce_festive_promo": [
                "diwali", "festive", "offer", "discount", "off", "promotion", "deals", "cashback",
                "sale", "celebration", "festivity", "bonus", "reward", "savings", "voucher", "coupon"
            ],
            "food_delivery_dining": [
                "food", "delivery", "restaurant", "order", "swiggy", "dining", "meal", "groceries",
                "dishes", "eats", "deliveries", "kitchen", "menu", "cuisine", "snack"
            ],
            "payments_fintech": [
                "payment", "upi", "cashback", "wallet", "phonepe", "transaction", "fintech",
                "merchant", "checkout", "transfer", "gateway", "digital", "qr", "refund"
            ],
            "banking_cards": [
                "credit", "card", "hdfc", "bank", "debit", "banking", "emi", "loan", "interest",
                "account", "points", "reward", "consumer", "privilege", "statement"
            ],
            "automotive_transport": [
                "automobile", "vehicle", "car", "bike", "motorcycle", "electric", "ev", "bajaj",
                "financing", "engine", "dealership", "test-drive", "scooter", "auto", "rides"
            ],
            "technology_cloud": [
                "software", "cloud", "api", "ai", "agent", "data", "platform", "server", "infra"
            ]
        }

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 1]
        return tokens

    def get_embedding(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        vec = np.zeros(self.dim, dtype=np.float32)

        if not tokens:
            # Return normalized pseudo-random vector based on text hash
            h = int(hashlib.md5(text.encode()).hexdigest(), 16)
            np.random.seed(h % (2**32))
            vec = np.random.randn(self.dim).astype(np.float32)
            norm = np.linalg.norm(vec)
            return (vec / (norm if norm > 0 else 1.0)).tolist()

        # 1. Project tokens onto semantic clusters
        for i, (domain, keywords) in enumerate(self.domains.items()):
            domain_offset = (i * (self.dim // len(self.domains))) % self.dim
            domain_weight = 0.0
            
            for token in tokens:
                for kw in keywords:
                    if kw in token or token in kw:
                        domain_weight += 1.5 if kw == token else 0.8
            
            if domain_weight > 0:
                # Distribute domain weight across assigned dimensions
                indices = [(domain_offset + j) % self.dim for j in range(32)]
                vec[indices] += domain_weight

        # 2. Add n-gram subword feature hashing for out-of-vocabulary semantic nuance
        for token in tokens:
            h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
            idx1 = h % self.dim
            idx2 = (h >> 8) % self.dim
            idx3 = (h >> 16) % self.dim
            sign = 1.0 if (h >> 24) % 2 == 0 else -1.0
            vec[idx1] += 0.3 * sign
            vec[idx2] += 0.2 * sign
            vec[idx3] += 0.1 * sign

        # 3. L2 normalize the embedding vector
        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return [round(float(x), 6) for x in vec]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = "models/text-embedding-004"

    def get_embedding(self, text: str) -> List[float]:
        import google.generativeai as genai
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="semantic_similarity"
        )
        return result["embedding"]

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self.get_embedding(t) for t in texts]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str, base_url: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "text-embedding-3-small"

    def get_embedding(self, text: str) -> List[float]:
        resp = self.client.embeddings.create(
            input=[text],
            model=self.model
        )
        return resp.data[0].embedding

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(
            input=texts,
            model=self.model
        )
        return [item.embedding for item in resp.data]


def get_embedding_provider() -> BaseEmbeddingProvider:
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            return GeminiEmbeddingProvider(api_key=settings.GEMINI_API_KEY)
        except Exception:
            pass
    elif provider == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAIEmbeddingProvider(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        except Exception:
            pass
    return DeterministicSemanticEmbeddingProvider(dim=settings.EMBEDDING_DIMENSION)
