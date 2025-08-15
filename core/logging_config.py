import logging
import sys

def configure_logging():
    """
    Configura el sistema de logging para toda la aplicación.
    - Registra en la consola con un formato simple.
    - Registra en un archivo (app.log) con un formato detallado.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s'
    )
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    print("Sistema de logging configurado.")
