import requests
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from ..utils.yaml_loader import get_prompt_loader

@dataclass
class AIServiceConfig:
    """Базовый класс конфигурации для AI сервисов"""
    api_key: str
    api_url: str
    default_model: str
    default_temperature: float = 0.7
    default_max_tokens: int = 1000
    timeout: int = 30

class AIModelService(ABC):
    """Абстрактный базовый класс для всех сервисов нейросетей"""
    
    def __init__(self, model_name: str, config: Optional[AIServiceConfig] = None):
        self.model_name = model_name
        
        self.prompt_loader = get_prompt_loader()
        self.config = config or self._get_default_config()
    
    @abstractmethod
    def _get_default_config(self) -> AIServiceConfig:
        """Возвращает конфигурацию по умолчанию для сервиса"""
        pass
    
    @abstractmethod
    def generate_response(
        self, 
        message: str, 
        prompt_template: Optional[str] = None, 
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Генерирует ответ от модели
        
        Args:
            message: Сообщение пользователя
            prompt_template: Имя шаблона промпта (из yaml-файлов)
            **kwargs: Дополнительные параметры для генерации
        
        Returns:
            dict: Ответ от модели
        """
        pass
    
    def get_prompt_template(self, prompt_name: str) -> Optional[Dict[str, Any]]:
        """Получает шаблон промпта из загрузчика"""
        return self.prompt_loader.get_prompt(self.model_name, prompt_name)
    
    def format_prompt(self, template: Any, **kwargs: Any) -> Any:
        """Форматирует промпт, подставляя переменные рекурсивно"""
        if isinstance(template, str):
            return template.format(**kwargs)
        elif isinstance(template, dict):
            result = {}
            for key, value in template.items():
                result[key] = self.format_prompt(value, **kwargs)
            return result
        elif isinstance(template, (list, tuple)):
            return [self.format_prompt(item, **kwargs) for item in template]
        else:
            return template
    
    def _make_api_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any], 
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет запрос к API с обработкой ошибок
        
        Args:
            endpoint: URL эндпоинта API
            data: Данные для отправки
            headers: Заголовки запроса
            
        Returns:
            dict: Ответ от API
            
        Raises:
            Exception: При ошибке запроса
        """
        try:
            headers = headers or {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                timeout=self.config.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка запроса к API {self.model_name}: {str(e)}"
            raise Exception(error_msg) from e
