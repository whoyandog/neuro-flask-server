from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

def create_app():
    try:
        app = Flask(__name__)
        
        app.config['JSON_AS_ASCII'] = False
        app.debug = True # Поменять на False в работе

        # Настройка корневого логгера
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Добавляем обработчик для вывода в консоль только к корневому логгеру
        if not root_logger.handlers:  # Предотвращаем дублирование обработчиков
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s'
            ))
            root_logger.addHandler(console_handler)
        
        # Настраиваем логгер приложения без добавления консольного обработчика
        app.logger.setLevel(logging.INFO)
        
        # Настраиваем логгер для сервисов без добавления консольного обработчика
        services_logger = logging.getLogger('neiro.services')
        services_logger.setLevel(logging.DEBUG)
        services_logger.propagate = True  # Обеспечиваем передачу сообщений к корневому логгеру
        
        if not app.debug:
            try:
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                
                # Файловый логгер для приложения
                app_file_handler = RotatingFileHandler('logs/neuro_flask.log', maxBytes=10240, backupCount=20, encoding='utf-8')
                app_file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                app_file_handler.setLevel(logging.INFO)
                app.logger.addHandler(app_file_handler)
                
                # Отдельный файловый логгер для трассировки сообщений и кодировки
                trace_file_handler = RotatingFileHandler('logs/message_trace.log', maxBytes=10240, backupCount=10, encoding='utf-8')
                trace_file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
                ))
                trace_file_handler.setLevel(logging.DEBUG)
                services_logger.addHandler(trace_file_handler)
                
                app.logger.info('Запуск Flask-сервера нейросетей')
            except Exception as e:
                app.logger.error(f'Ошибка при настройке файлового логирования: {str(e)}')
        
        try:
            from .utils.yaml_loader import init_prompt_loader
            prompt_loader = init_prompt_loader()
            app.logger.info(f'Загружено промптов: {sum(len(prompts) for prompts in prompt_loader.prompts.values())}')
        except Exception as e:
            app.logger.error(f'Ошибка при загрузке промптов: {str(e)}')
            raise
        
        from .api.routes import main_routes
        app.register_blueprint(main_routes)
        
        return app
    except Exception as e:
        print(f"Критическая ошибка при создании приложения: {str(e)}")
        raise
