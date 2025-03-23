from typing import Dict, List, Type
from ..services import (
    AIModelService,
    ChatGPTService,
    DeepSeekService,
    OpenRouterDeepSeekService
)

class AIServiceFactory:
    """Фабрика для создания сервисов нейросетей"""
    
    _services: Dict[str, Type[AIModelService]] = {
        "chatgpt": ChatGPTService,
        "deepseek": DeepSeekService,
        "openrouter-deepseek": OpenRouterDeepSeekService
    }
    
    @classmethod
    def get_service(cls, model_name: str) -> AIModelService:
        """
        Возвращает экземпляр сервиса для указанной модели
        
        Args:
            model_name: Имя модели
            
        Returns:
            AIModelService: Экземпляр сервиса
            
        Raises:
            ValueError: Если модель не найдена
        """
        if model_name not in cls._services:
            available_models = ", ".join(cls._services.keys())
            raise ValueError(f"Модель '{model_name}' не найдена. Доступные модели: {available_models}")
        
        return cls._services[model_name]()
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Возвращает список доступных моделей"""
        return list(cls._services.keys())