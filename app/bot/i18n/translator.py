from locales.en.txt import EN
from locales.ru.txt import RU


def get_translator() -> dict[str, str | dict[str, str]]:
    return {
        'default': 'ru',
        'ru': RU,
        'en': EN
    }