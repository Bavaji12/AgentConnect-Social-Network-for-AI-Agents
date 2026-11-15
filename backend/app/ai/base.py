from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class BaseEmbeddingProvider(ABC):
    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for a single text."""
        pass

    @abstractmethod
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for multiple texts."""
        pass

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """Generate text completion from LLM."""
        pass

    @abstractmethod
    def evaluate_relevance(
        self,
        post_title: str,
        post_content: str,
        agent_name: str,
        company_name: str,
        industry: str,
        manifesto: str
    ) -> Dict[str, Any]:
        """
        Evaluate business relevance of a post for an agent.
        Returns dict with keys: 'relevance_score' (0-1), 'explanation' (str)
        """
        pass
