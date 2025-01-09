import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("django-info")


def get_currency_rates() -> Optional[Dict[str, Dict[str, Union[float, str]]]]:
    """
    Получает курсы валют с сайта ЦБ РФ и их изменение за последние два дня.

    Returns:
    Optional[Dict[str, Dict[str, Union[float, str]]]]:
    Словарь с информацией о курсах валют. Каждая валюта представлена словарем со следующими ключами:

    - 'current_rate' (float): Текущий курс валюты к рублю.
        Пример: 14.5678 (курс 1 китайского юаня в рублях)

    - 'change' (float): Абсолютное изменение курса за последний день.
        Положительное значение означает рост курса,
        отрицательное - падение.
        Пример: 0.0123 (курс вырос на 0.0123 рубля)

    - 'change_percentage' (float): Относительное изменение курса в процентах.
        Показывает процент изменения курса за последний день.
        Пример: 0.84 (курс вырос на 0.84%)

    Возвращает None в случае ошибки получения данных.
    """
    try:
        # Получаем текущую дату и дату предыдущего дня
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        # Форматируем даты для URL
        today_str = today.strftime("%d/%m/%Y")
        yesterday_str = yesterday.strftime("%d/%m/%Y")

        # URL для получения курсов валют
        url_today = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={today_str}"
        url_yesterday = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={yesterday_str}"

        # Получаем XML с курсами валют
        response_today = requests.get(url_today)
        response_yesterday = requests.get(url_yesterday)

        # Парсим XML
        root_today = ET.fromstring(response_today.content)
        root_yesterday = ET.fromstring(response_yesterday.content)

        # Функция для поиска валюты в XML
        def find_currency(root, currency_code):
            for valute in root.findall('Valute'):
                if valute.find('CharCode').text == currency_code:
                    value = valute.find('Value').text.replace(',', '.')
                    nominal = int(valute.find('Nominal').text)
                    return float(value) / nominal
            return None

        # Получаем курсы валют
        currencies = ['CNY', 'EUR', 'USD']
        rates = {}

        for currency in currencies:
            today_rate = find_currency(root_today, currency)
            yesterday_rate = find_currency(root_yesterday, currency)

            if today_rate is not None and yesterday_rate is not None:
                rates[currency] = {
                    'current_rate': round(today_rate, 4),
                    'change': round(today_rate - yesterday_rate, 4),
                    'change_percentage': round(((today_rate - yesterday_rate) / yesterday_rate) * 100, 2)
                }

        return rates

    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {e}")
        return None


def get_key_rate_change() -> Dict[str, Union[str, float, None]] or None:
    """
    Получает информацию об изменении ключевой ставки Центрального Банка РФ за последний год.

    Returns:
    Dict[str, Union[str, float, None]]: Словарь с подробной информацией об изменении ключевой ставки.
    """
    try:
        # Расчет даты от текущей даты
        current_date = datetime.now()
        one_year_ago = current_date - timedelta(days=60)

        # Форматирование дат для запроса
        from_date = one_year_ago.strftime("%d.%m.%Y")
        to_date = current_date.strftime("%d.%m.%Y")

        url = "https://www.cbr.ru/hd_base/KeyRate/"

        # Параметры запроса
        params = {
            "UniDbQuery.Posted": "True",
            "UniDbQuery.From": from_date,
            "UniDbQuery.To": to_date
        }

        # Выполнение запроса с параметрами
        response = requests.get(url, params=params)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Найти таблицу с данными о ставке
        table = soup.find("table", class_="data")
        if not table:
            raise ValueError("Таблица с данными не найдена.")

        rows = table.find_all("tr")[1:]  # Пропускаем заголовок таблицы
        if len(rows) < 2:
            raise ValueError("Недостаточно данных для анализа.")

        # Парсим строки таблицы
        rates = []
        for row in rows:
            cols = row.find_all("td")
            date = cols[0].get_text(strip=True)
            rate = cols[1].get_text(strip=True)
            try:
                rates.append((date, float(rate.replace(",", "."))))
            except ValueError:
                continue

        if len(rates) < 2:
            raise ValueError("Недостаточно данных для расчета изменения.")

        # Текущее значение
        current_date, current_rate = rates[0]
        logger.debug(rates)

        # Найти первую дату текущего значения
        first_current_rate_date = current_date
        for i in range(len(rates) - 1):
            if rates[i + 1][1] != rates[i][1]:
                first_current_rate_date = rates[i][0]

        # Найти первое предыдущее значение, отличное от текущего
        previous_date, previous_rate = rates[0]
        for date, rate in rates[1:]:
            if rate != current_rate:
                previous_date, previous_rate = date, rate
                break

        # Расчёт изменения
        change = current_rate - previous_rate
        change_percentage = (change / previous_rate) * 100 if previous_rate != 0 else None

        return {
            "current_rate": current_rate,
            "change": round(change, 2),
            "change_percentage": round(change_percentage, 2) if change_percentage is not None else None,
            "last_change_date": first_current_rate_date
        }

    except Exception as e:
        logger.error(f"Ошибка при получении ключевой ставки: {e}")
        return None


def get_combined_financial_rates() -> Optional[Dict[str, Dict[str, Union[float, str, None]]]]:
    """
    Объединяет результаты получения курсов валют и ключевой ставки ЦБ РФ.

    Returns:
    Optional[Dict[str, Dict[str, Union[float, str, None]]]]:
    Словарь с информацией о курсах валют и ключевой ставке в едином формате.

    Структура возвращаемого словаря:
    {
        'CNY': {
            'current_rate': float,
            'change': float,
            'change_percentage': float
        },
        'EUR': {...},
        'USD': {...},
        'KEY_RATE': {
            'current_rate': float,
            'change': float,
            'change_percentage': float or None
        }
    }

    Возвращает None в случае ошибки получения данных.
    """
    try:
        # Получаем курсы валют
        currency_rates = get_currency_rates()

        # Получаем ключевую ставку
        key_rate = get_key_rate_change()

        # Если не удалось получить какие-либо данные, возвращаем None
        if currency_rates is None or key_rate is None:
            return None

        # Добавляем ключевую ставку в словарь
        currency_rates['KEY_RATE'] = {
            'current_rate': key_rate['current_rate'],
            'change': key_rate['change'],
            'change_percentage': key_rate['change_percentage'],
            'last_change_date': key_rate['last_change_date']
        }
        logger.info(currency_rates)
        return currency_rates

    except Exception as e:
        logger.error(f"Ошибка при объединении финансовых данных: {e}")
        return None


# Пример использования
if __name__ == "__main__":
    import json

    combined_rates = get_combined_financial_rates()
    if combined_rates:
        print(json.dumps(combined_rates, indent=2, ensure_ascii=False))
