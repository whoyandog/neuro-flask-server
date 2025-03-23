import sys
import logging
from flask import Flask
from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        app = create_app()
        logger.info("Приложение успешно создано, запускаем сервер...")
        app.run(host='localhost', port=5151)
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {str(e)}", exc_info=True)
        sys.exit(1)
