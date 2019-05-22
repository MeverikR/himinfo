"""
Различные полезные утилиты
"""


def decode_dict(d: dict) -> dict:
    """
    Urldecode по всем значениям словарика
    :param d:
    :return:
    """
    if not d:
        return {}
    if len(d) <= 0:
        return {}

    from urllib.parse import unquote
    for k,v in d.items():
        if type(v) == str:
            d[k] = unquote(v)

    return d