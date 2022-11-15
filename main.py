import os
import shutil
import time
import requests
import pandas as pd

from typing import Union, Dict, List
from loguru import logger
from dotenv import load_dotenv

from schema import Product
from utils import start_logging

load_dotenv()

TOKEN_API = os.environ.get("TOKEN_API")
URL_REQUEST = 'https://santop.su/json/'
WAREHOUSE = 254
NAME_FILE_RESULT = 'santopsu.xlsx'
DIR_SERVER = '/home/bitrix/www/upload/'


def get_data_api(url: str, token: str, vendor: int = 0, warehouses: int = 254, available: int = 0) -> Union[Dict, None]:
    params = {
        'token': token,
        'vendor': vendor,
        'warehouses': warehouses,
        'available': available
    }

    count = 1
    while count <= 3:
        try:
            logger.debug(f'Получаем данные из API, url {url}, попытка {count}')
            response = requests.get(url=url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f'Ошибка ответа сервера - {response.status_code} \n{response.text}')
                count += 1
                time.sleep(5)
                continue
        except requests.exceptions.Timeout:
            count += 1
            time.sleep(10)
            continue

    logger.error(f'Не удалось получить данные из API за отведенное кол-во попыток')
    return None


def parsing_response(response: Dict = None) -> (Dict, int):
    products = {}
    pages = 0
    if response:
        if 'result' in response and response['result'] == 'success':
            if 'pages' in response and response['pages']:
                pages = response['pages']
            if 'products' in response and response['products']:
                products = {**products, **response['products']}

    return products, pages


def get_products():
    url = URL_REQUEST + 'page0'
    response = get_data_api(url=url, token=TOKEN_API)
    # получаем товары с первой страницы и кол-во всего страниц
    products, pages = parsing_response(response=response)

    # получаем товары с остальных страниц
    for i in range(1, pages):
        url = URL_REQUEST + 'page' + str(i)
        response = get_data_api(url=url, token=TOKEN_API)
        # объединяем словари
        products = {**products, **parsing_response(response=response)[0]}
        time.sleep(1)

    return products


def create_list_dict(products: Dict) -> List[Dict]:
    result = []
    for key, value in products.items():
        product = Product(**value).dict()
        if product['warehouses']:
            product['warehouses_id'] = product['warehouses'][0].get('id', '')
            product['warehouses_name'] = product['warehouses'][0].get('name', '')
            product['warehouses_quantity'] = int(product['warehouses'][0].get('quantity', 0))
            del product['warehouses']
            result.append(product)

    return result


def main():
    products = get_products()
    products = create_list_dict(products)
    logger.info(f'Сформирован общий список товаров из API. Всего товаров {len(products)}')
    df_products = pd.DataFrame(products)
    df_products.to_excel(excel_writer=NAME_FILE_RESULT, sheet_name='Products', index=False, engine='xlsxwriter')

    shutil.copyfile(NAME_FILE_RESULT, DIR_SERVER + NAME_FILE_RESULT)


if __name__ == '__main__':
    start_logging(name_dir='logs', name_log_file='debug_main.log')  # устанавливаем параметры для логирования
    logger.info(f'Запуск скрипта получения товаров из API santop.su')
    try:
        main()
        logger.success('Успешное завершение работы скрипта')
    except Exception as ex:
        logger.exception(f'Скрипт завершил работу с ошибкой. Обратитесь к разработчику.\n{ex}')
