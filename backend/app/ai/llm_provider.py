import json
import logging
import re
from typing import Dict, Any, Optional
from app.core.config import settings
from app.ai.base import BaseLLMProvider

logger = logging.getLogger("agentconnect.ai.llm")

class DeterministicLLMProvider(BaseLLMProvider):
    """
    High-fidelity deterministic LLM provider.
    Provides realistic, contextual agent responses, commercial partnership proposals,
    and business relevance explanations for demo and offline test environments.
    """
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        combined = f"{prompt} {system_prompt or ''}".lower()
        
        # Tailored high-quality responses for the core enterprise benchmark agents
        if "phonepe" in combined:
            if "diwali" in combined or "swiggy" in combined or "food" in combined:
                return "PhonePe offers an additional ₹50 cashback when users pay for Swiggy orders using PhonePe UPI during Diwali."
            return "PhonePe is eager to partner on seamless 1-click UPI checkout and merchant cashback rewards for this campaign."
            
        elif "hdfc" in combined:
            if "diwali" in combined or "swiggy" in combined or "food" in combined:
                return "HDFC Bank cardholders get an exclusive 10% instant discount (up to ₹150) on festive food deliveries with HDFC Credit Cards."
            return "HDFC Bank proposes a co-branded card promotion offering 5X reward points on all campaign transactions."
            
        elif "bajaj" in combined:
            return "Bajaj Auto notes the promotional update and evaluates potential fleet electrification partnerships for delivery partners."
            
        # Generic contextual generator for any custom dynamic agent
        return (
            "We are interested in exploring synergy with this initiative. "
            "Our platform can provide value-added integrations to enhance user retention and merchant conversion."
        )

    def evaluate_relevance(
        self,
        post_title: str,
        post_content: str,
        agent_name: str,
        company_name: str,
        industry: str,
        manifesto: str
    ) -> Dict[str, Any]:
        combined_post = f"{post_title} {post_content}".lower()
        combined_agent = f"{agent_name} {company_name} {industry} {manifesto}".lower()

        # Check for core synergy keywords
        commerce_promo_match = any(w in combined_post for w in ["diwali", "festive", "offer", "discount", "off", "promotion", "cashback", "sale"])
        food_delivery_match = any(w in combined_post for w in ["food", "delivery", "swiggy", "restaurant", "order"])
        
        payment_synergy = any(w in combined_agent for w in ["upi", "payment", "cashback", "fintech", "wallet", "merchant", "checkout"])
        banking_synergy = any(w in combined_agent for w in ["credit card", "bank", "card", "banking", "points", "reward"])
        auto_synergy = any(w in combined_agent for w in ["automobile", "vehicle", "car", "bike", "motorcycle", "ev"])

        score = 0.50
        explanation_parts = []

        if commerce_promo_match and (payment_synergy or banking_synergy):
            score = 0.88 if payment_synergy else 0.84
            explanation_parts.append(
                f"High commercial synergy: {company_name} operates in {industry} and specializes in merchant payment incentives "
                f"which directly complement festive consumer campaigns like '{post_title}'."
            )
        elif auto_synergy and food_delivery_match:
            score = 0.38
            explanation_parts.append(
                f"Low direct relevance: {company_name} focuses on {industry} and automotive financing, "
                f"which lacks immediate transaction-level consumer synergy with '{post_title}'."
            )
        else:
            # Overlap calculation
            post_words = set(re.findall(r"\w{4,}", combined_post))
            agent_words = set(re.findall(r"\w{4,}", combined_agent))
            overlap = post_words.intersection(agent_words)
            if overlap:
                score = min(0.85, 0.5 + (len(overlap) * 0.08))
                explanation_parts.append(f"Matching operational terms found: {', '.join(list(overlap)[:4])}.")
            else:
                score = 0.42
                explanation_parts.append(f"Limited thematic intersection between {industry} and post domain.")

        return {
            "relevance_score": round(score, 4),
            "explanation": " ".join(explanation_parts)
        }


class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        full_prompt = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
        response = self.model.generate_content(full_prompt)
        return response.text.strip()

    def evaluate_relevance(
        self,
        post_title: str,
        post_content: str,
        agent_name: str,
        company_name: str,
        industry: str,
        manifesto: str
    ) -> Dict[str, Any]:
        prompt = f"""
You are an enterprise AI Agent router. Evaluate whether the following post is commercially relevant to the target agent.
Post Title: {post_title}
Post Content: {post_content}

Target Agent:
Name: {agent_name}
Company: {company_name}
Industry: {industry}
Manifesto: {manifesto}

Respond strictly in JSON format with two keys:
"relevance_score": float between 0.0 and 1.0
"explanation": a clear concise business explanation (1-2 sentences)
"""
        resp = self.model.generate_content(prompt)
        try:
            cleaned = resp.text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:-3].strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:-3].strip()
            data = json.loads(cleaned)
            return {
                "relevance_score": float(data.get("relevance_score", 0.5)),
                "explanation": str(data.get("explanation", "Evaluated by Gemini."))
            }
        except Exception as e:
            logger.warning(f"Error parsing Gemini JSON: {e}, falling back to deterministic evaluation.")
            return DeterministicLLMProvider().evaluate_relevance(
                post_title, post_content, agent_name, company_name, industry, manifesto
            )


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str, base_url: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = "gpt-4o-mini"

    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def evaluate_relevance(
        self,
        post_title: str,
        post_content: str,
        agent_name: str,
        company_name: str,
        industry: str,
        manifesto: str
    ) -> Dict[str, Any]:
        prompt = f"""Evaluate relevance of the post for this agent:
Post Title: {post_title}
Post Content: {post_content}
Agent: {agent_name} ({company_name}) in {industry}
Manifesto: {manifesto}

Return JSON with:
"relevance_score": float 0.0 to 1.0
"explanation": concise business justification
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content)
            return {
                "relevance_score": float(data.get("relevance_score", 0.5)),
                "explanation": str(data.get("explanation", "Evaluated by OpenAI."))
            }
        except Exception as e:
            logger.warning(f"Error in OpenAI evaluation: {e}")
            return DeterministicLLMProvider().evaluate_relevance(
                post_title, post_content, agent_name, company_name, industry, manifesto
            )


def get_llm_provider() -> BaseLLMProvider:
    provider = settings.LLM_PROVIDER.lower()
    if provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            return GeminiLLMProvider(api_key=settings.GEMINI_API_KEY)
        except Exception:
            pass
    elif provider == "openai" and settings.OPENAI_API_KEY:
        try:
            return OpenAILLMProvider(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        except Exception:
            pass
    return DeterministicLLMProvider()
