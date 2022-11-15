import os

from pathlib import Path
from loguru import logger


def start_logging(name_dir, name_log_file):
    """
    Проверяем наличие директории для логов и создаем при необходимости,
    формируем путь до лог файла и устанавливаем параметры для логирования
    """
    if not os.path.isdir(name_dir):
        os.mkdir(name_dir)
    path_log = Path(Path.cwd(), name_dir, name_log_file)
    logger.add(path_log, level='DEBUG', compression="zip", rotation="10 MB", retention="1 week", encoding='utf-8')
