import logging
import sys

def configure_logging():
    """
    Configura el sistema de logging para toda la aplicación.
    - Registra en la consola con un formato simple.
    - Registra en un archivo (app.log) con un formato detallado.
    """
    # Crear un logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Nivel mínimo de registro

    # Prevenir la duplicación de handlers si la función se llama varias veces
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Formateadores ---
    # Formato para el archivo (más detallado)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s'
    )
    # Formato para la consola (más simple)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # --- Handlers ---
    # Handler para la consola (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Handler para el archivo
    file_handler = logging.FileHandler('app.log', mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG) # Registrar todo (desde DEBUG hacia arriba) en el archivo
    file_handler.setFormatter(file_formatter)

    # Añadir handlers al logger principal
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    print("Sistema de logging configurado.")
