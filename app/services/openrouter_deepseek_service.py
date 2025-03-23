import os
from typing import Any, Dict, Optional
from dataclasses import dataclass
from .base import AIModelService, AIServiceConfig

@dataclass
class OpenRouterDeepSeekConfig(AIServiceConfig):
    """Конфигурация для OpenRouter DeepSeek сервиса"""
    api_key: str = os.environ.get("OPENROUTER_DEEPSEEK_API_KEY", "")
    api_url: str = "https://openrouter.ai/api/v1/chat/completions"
    default_model: str = "deepseek/deepseek-r1-zero:free"

class OpenRouterDeepSeekService(AIModelService):
    """Сервис для работы с OpenRouter DeepSeek API"""

    def __init__(self, config: Optional[OpenRouterDeepSeekConfig] = None):
        super().__init__("openrouter-deepseek", config)

    def _get_default_config(self) -> OpenRouterDeepSeekConfig:
        return OpenRouterDeepSeekConfig()
    
    def generate_response(
        self, 
        message: str, 
        prompt_template: Optional[str] = None, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        if not self.config.api_key:
            return {"error": "API ключ Openrouter Deepseek не настроен"}
        
        if prompt_template:
            template_data = self.get_prompt_template(prompt_template)
            if not template_data:
                return {"error": f"Шаблон промпта '{prompt_template}' не найден"}
            
            prompt_data = self.format_prompt(
                template_data, 
                message=message,
                **kwargs
            )
        else:
            prompt_data = {
                "model": kwargs.get("model", self.config.default_model),
                "messages": [{"role": "user", "content": message}],
                "temperature": kwargs.get("temperature", self.config.default_temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.default_max_tokens)
            }
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        response = self._make_api_request(self.config.api_url, prompt_data, headers)
        return response
