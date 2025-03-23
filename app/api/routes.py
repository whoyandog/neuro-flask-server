from flask import Blueprint, request, jsonify, current_app
from ..factories.ai_service_factory import AIServiceFactory
from ..utils.yaml_loader import get_prompt_loader

main_routes = Blueprint('main', __name__)

@main_routes.route('/api/process', methods=['POST'])
def process_message():
    """
    Обрабатывает сообщение и отправляет его к выбранной нейросети
    
    Ожидаемый JSON:
    {
        "model": "chatgpt",      // Имя модели (chatgpt, deepseek, etc)
        "message": "Привет!",    // Текст сообщения пользователя
        "prompt_template": "base", // (опционально) Имя шаблона промпта
        "parameters": {}         // (опционально) Дополнительные параметры
    }
    """

    try:
        data = request.json
        
        if not data:
            current_app.logger.warning("Отсутствуют данные запроса")
            return jsonify({"error": "Отсутствуют данные запроса"}), 400
            
        if 'model' not in data:
            current_app.logger.warning("Не указана модель")
            return jsonify({"error": "Не указана модель"}), 400
            
        if 'message' not in data:
            current_app.logger.warning("Отсутствует сообщение")
            return jsonify({"error": "Отсутствует сообщение"}), 400
        
        try:
            service = AIServiceFactory.get_service(data['model'])
        except ValueError as e:
            current_app.logger.error(f"Ошибка создания сервиса: {str(e)}")
            return jsonify({"error": str(e)}), 400
        
        response = service.generate_response(
            message=data['message'],
            prompt_template=data.get('prompt_template'),
            **(data.get('parameters', {}))
        )
        
        
        if "error" in response:
            current_app.logger.error(f"Ошибка в ответе нейросети: {response['error']}")
            return jsonify(response), 400
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при обработке запроса: {str(e)}", exc_info=True)
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500


@main_routes.route('/api/models', methods=['GET'])
def list_models():
    """Возвращает список доступных моделей"""
    return jsonify({
        "models": AIServiceFactory.get_available_models()
    })


@main_routes.route('/api/prompts', methods=['GET'])
def list_prompts():
    """Возвращает список доступных промптов для всех моделей"""
    prompt_loader = get_prompt_loader()
    return jsonify(prompt_loader.prompts)


@main_routes.route('/api/prompts/<model_name>', methods=['GET'])
def list_model_prompts(model_name):
    """Возвращает список доступных промптов для указанной модели"""
    prompt_loader = get_prompt_loader()
    if model_name in prompt_loader.prompts:
        return jsonify(prompt_loader.prompts[model_name])
    return jsonify({"error": f"Модель {model_name} не найдена"}), 404


@main_routes.route('/api/reload', methods=['POST'])
def reload_prompts():
    """Перезагружает все промпты"""
    prompt_loader = get_prompt_loader()
    prompt_loader.load_all_prompts()
    return jsonify({"status": "success", "message": "Промпты перезагружены"}) 