"""
Gemini Multimodal Client Module
Handles multimodal vision and text inference with Google Gemini models,
with robust JSON response extraction and graceful fallback to local engineering demo mode.
"""

import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from PIL import Image

logger = logging.getLogger(__name__)

# Model configurations
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
DEFAULT_MODEL = "gemini-1.5-flash"


def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON from potentially noisy model output.
    Handles markdown code fences, leading/trailing text, and minor formatting issues.
    """
    if not raw_text:
        raise ValueError("Empty response received from model")

    text = raw_text.strip()

    # Match ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if match:
        text = match.group(1).strip()

    # If the text has surrounding text before the first '{' and after the last '}'
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace : last_brace + 1]

    # Attempt direct json.loads
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Try minor cleanup for common LLM quirks: trailing commas before } or ]
        cleaned = re.sub(r",\s*([\]}])", r"\1", text)
        try:
            return json.loads(cleaned)
        except Exception:
            logger.error("Failed to parse cleaned JSON: %s (Raw: %s)", cleaned, raw_text[:200])
            raise exc


class GeminiMultimodalClient:
    """
    Wraps Google Gemini Multimodal APIs with graceful fallback to simulated demo mode.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = DEFAULT_MODEL):
        effective_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        if not effective_key:
            try:
                import streamlit as st
                effective_key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
            except Exception:
                effective_key = ""
        self.api_key = effective_key
        self.model_name = model_name
        self.client_type = None
        self._genai_client = None
        self._legacy_model = None

        if self.api_key:
            self._init_client()

    def _init_client(self) -> None:
        """Attempts to initialize google.genai or google.generativeai."""
        # Try modern google.genai first
        try:
            from google import genai
            self._genai_client = genai.Client(api_key=self.api_key)
            self.client_type = "google-genai"
            return
        except Exception as e1:
            logger.debug("Could not initialize google.genai: %s. Trying legacy.", e1)

        # Fallback to legacy google.generativeai
        try:
            import google.generativeai as legacy_genai
            legacy_genai.configure(api_key=self.api_key)
            self._legacy_model = legacy_genai.GenerativeModel(self.model_name)
            self.client_type = "google-generativeai"
        except Exception as e2:
            logger.warning("Failed to initialize Google GenAI SDK: %s", e2)
            self.client_type = None

    @property
    def is_live(self) -> bool:
        """True if a valid Gemini client could be initialized with an API key."""
        return bool(self.api_key and self.client_type)

    def analyze_image_json(
        self,
        image: Image.Image,
        prompt: str,
        fallback_handler: Optional[callable] = None,
        **fallback_kwargs,
    ) -> Tuple[Dict[str, Any], bool, str]:
        """
        Executes multimodal visual analysis expecting a structured JSON response.
        Returns:
            (result_dict, is_live_call, status_message)
        """
        if not self.is_live:
            if fallback_handler:
                mock_res = fallback_handler(**fallback_kwargs)
                return mock_res, False, "Demo Mode: High-fidelity simulation active (No Gemini API key supplied)."
            return {"error": "API key required and no fallback registered"}, False, "No API key"

        try:
            raw_text = ""
            if self.client_type == "google-genai":
                response = self._genai_client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, image],
                )
                raw_text = getattr(response, "text", "") or str(response)
            elif self.client_type == "google-generativeai":
                response = self._legacy_model.generate_content([prompt, image])
                raw_text = getattr(response, "text", "") or str(response)

            parsed = clean_json_response(raw_text)
            return parsed, True, f"Live Gemini Analysis completed using {self.model_name}."

        except Exception as exc:
            logger.warning("Live Gemini inference encountered error: %s. Falling back to demo mode.", exc)
            if fallback_handler:
                mock_res = fallback_handler(**fallback_kwargs)
                return (
                    mock_res,
                    False,
                    f"Notice: Live API call returned error ({str(exc)[:120]}...). Switched to fallback demo engine.",
                )
            return {"error": str(exc)}, False, f"API Error: {exc}"

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_instruction: str = "",
        fallback_handler: Optional[callable] = None,
        **fallback_kwargs,
    ) -> Tuple[str, bool, str]:
        """
        Generates conversational chat completion.
        Returns:
            (reply_text, is_live_call, status_message)
        """
        if not self.is_live:
            if fallback_handler:
                reply = fallback_handler(messages=messages, **fallback_kwargs)
                return reply, False, "Demo Mode: Civil engineering assistant responses active."
            return "Please provide a valid Gemini API key in the sidebar.", False, "Demo Mode"

        try:
            # Format prompt with history
            formatted_prompt = f"System Instruction:\n{system_instruction}\n\nConversation History:\n"
            for m in messages:
                role = "Site Engineer" if m.get("role") == "user" else "AI Specialist"
                formatted_prompt += f"{role}: {m.get('content')}\n"
            formatted_prompt += "AI Specialist: "

            reply_text = ""
            if self.client_type == "google-genai":
                response = self._genai_client.models.generate_content(
                    model=self.model_name,
                    contents=formatted_prompt,
                )
                reply_text = getattr(response, "text", "") or str(response)
            elif self.client_type == "google-generativeai":
                response = self._legacy_model.generate_content(formatted_prompt)
                reply_text = getattr(response, "text", "") or str(response)

            return reply_text.strip(), True, f"Response generated via live {self.model_name}."

        except Exception as exc:
            logger.warning("Chat completion failed: %s. Reverting to fallback.", exc)
            if fallback_handler:
                reply = fallback_handler(messages=messages, **fallback_kwargs)
                return (
                    reply,
                    False,
                    f"Reverted to demo engine due to API condition ({str(exc)[:90]}).",
                )
            return f"Error connecting to Gemini API: {exc}", False, "API Error"
