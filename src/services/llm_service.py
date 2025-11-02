"""LLM service for interacting with various LLM providers."""

import logging
from typing import List, Dict, Any, Optional
import os

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with LLM providers."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients based on available API keys."""
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
        
        if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
            try:
                self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                logger.info("Anthropic client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic client: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        model: str = "gpt-4",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_message: Optional[str] = None
    ) -> str:
        """Generate response from LLM.
        
        Args:
            prompt: User prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_message: Optional system message
        
        Returns:
            Generated text response
        """
        logger.info(f"Generating response with model: {model}")
        
        if model.startswith("gpt"):
            return await self._openai_generate(prompt, model, max_tokens, temperature, system_message)
        elif model.startswith("claude"):
            return await self._anthropic_generate(prompt, model, max_tokens, temperature, system_message)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    async def _openai_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_message: Optional[str]
    ) -> str:
        """Generate response using OpenAI."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized. Set OPENAI_API_KEY environment variable.")
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _anthropic_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        system_message: Optional[str]
    ) -> str:
        """Generate response using Anthropic."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            response = self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message or "",
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
        
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def is_available(self, model: str) -> bool:
        """Check if a model is available.
        
        Args:
            model: Model name to check
        
        Returns:
            True if model is available
        """
        if model.startswith("gpt"):
            return self.openai_client is not None
        elif model.startswith("claude"):
            return self.anthropic_client is not None
        return False