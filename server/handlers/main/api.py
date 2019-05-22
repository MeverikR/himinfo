import logging
from aiohttp import web
from helpers.config import Config
from helpers.agbis_api import CustomApi
from helpers.data_api import Dataapi
from datetime import datetime, timedelta
from helpers.models.data import Data
from helpers.db import get_row
from helpers.models.user import User

config = Config.get_config()
CustomApi = CustomApi()
Dataapi = Dataapi()
logger = logging.getLogger('agbis')


async def api(db) -> dict:
    """
    В теории этот метод перебирает все строчки таблички Data
    И ищет по АОНУ в ответе CoMagic
    :param db:
    :return:
    """

    _log_ = {
        'phones_analyzed': 0,
        'communications_found': 0,
        'tags_applied': 0,
        'tags_removed_updated': 0,
        'problems': 0,
        'log': []
    }
    try:
        if not db:
            logging.debug('token not found')
            return {
                'success': False,
                'message': 'ERROR: No DB found.'
            }
        date_till = datetime.now().isoformat()
        date_from = (datetime.now() + timedelta(days=-30)).isoformat()
        date_out = (date_till.replace('T', ' ')).split('.')
        date_to = (date_from.replace('T', ' ')).split('.')
        gt_token = await get_row(User.get_tokens(), db)
        event = gt_token[0]
        token = event['token']
        if not token:
            return {
                'success': False,
                'message': 'ERROR: No token for user found.'
            }
        data = await Dataapi.calls(token, date_to[0], date_out[0])
        agbis_db_rows = await get_row(Data.get_select(), db)
        if len(agbis_db_rows) <= 0:
            return {
                'success': False,
                'message': 'ERROR: No data in DB found. PLease update DB using update_db query param'
            }
        if 'result' not in data:
            return {
                'success': False,
                'message': 'ERROR: No result in CoMagic answer'
            }
        if 'data' not in data['result']:
            return {
                'success': False,
                'message': 'ERROR: No data in CoMagic answer result'
            }
        # перебираем нашу табличку
        print('Total rows in DB: ' + str(len(agbis_db_rows)))
        for row in agbis_db_rows:
            _log_['phones_analyzed'] += 1
            row = dict(row)
            print('Analysing row with phone: ' + str(row.get('fone_cell')))
            print(row)
            phone = str(row.get('fone_cell'))
            found_phones_coms = []
            # ищем в ответе CoMagic все обращения с этого номера
            comagic_answer = data['result']['data']

            for elem in comagic_answer:
                if phone == elem.get('contact_phone_number') and elem.get('is_lost') is False:
                    comm_id = elem.get('communication_id')
                    if not comm_id:
                        return {
                            'success': False,
                            'message': 'ERROR! Comagic send data without communication_id'
                        }
                    _log_['communications_found'] += 1
                    print('OK! Found AON [' + phone + '] with communication [' + str(comm_id) + ']')
                    found_phones_coms.append(elem)
            if len(found_phones_coms) <= 0:
                print('WARNING! No communications found for AON: [' + phone + ']')
                _log_['log'].append({phone: 'not found'})
                continue  # идем смотреть следующий номер в БД
            print('Search for aon: [' + phone + '] complete, found: [' + str(
                len(found_phones_coms)) + '] communications, using FIRST!')
            com_for_sale = found_phones_coms[0]  # сказали брать первый
            print('FIRST Communication detected: [' + str(com_for_sale.get('communication_id')) +
                  ' date [' + com_for_sale.get('start_time') + ']')
            tags = com_for_sale.get('tags')
            date_pay = datetime.isoformat(row.get('date_pay')).replace('T', ' ')
            if tags:
                if tags[0]['tag_id'] == 1555 and float(com_for_sale.get('sale_cost')) == float(row.get('debet')):
                    _log_['problems'] += 1
                    print('WARNING! Tag already seted with this sale_cost')
                    print(row)
                    print(com_for_sale)
                    logging.debug('check ' + str(com_for_sale.get('communication_id')) + ' ' + date_till)
                    _log_['log'].append({phone: str(com_for_sale.get('communication_id')),
                                         'problem': True})
                elif tags[0]['tag_id'] == 1555:
                    # тег уже стоит - заменяем его
                    _log_['tags_removed_updated'] += 1
                    tags_del = await Dataapi.tag_delete(token, com_for_sale.get('communication_id'))
                    data_tag = await Dataapi.tag_sales('set.tag_sales',
                                                       token,
                                                       com_for_sale.get('communication_id'),
                                                       date_pay,
                                                       float(row.get('debet')), row.get('comment'))
                    _log_['log'].append(
                        {
                            phone: str(com_for_sale.get('communication_id')),
                            'debet': row.get('debet'),
                            'data': data_tag.get('result').get('data').get('id'),
                            'updated': True,
                            'date': com_for_sale.get('start_time'),
                        }
                    )
                else:
                    # :)
                    _log_['tags_applied'] += 1
                    data_tag_2 = await Dataapi.tag_sales('set.tag_sales',
                                                         token,
                                                         com_for_sale.get('communication_id'),
                                                         date_pay,
                                                         float(row.get('debet')), row.get('comment'))
                    _log_['log'].append({phone: str(com_for_sale.get('communication_id')),
                                         'debet': row.get('debet'),
                                         'data': data_tag_2.get('result').get('data').get('id'),
                                         'updated': False, 'date': com_for_sale.get('start_time'), })
            else:
                _log_['tags_applied'] += 1
                # первичная установка тега, когда ранее тега там не было
                data_tag_3 = await Dataapi.tag_sales('set.tag_sales',
                                                     token,
                                                     com_for_sale.get('communication_id'),
                                                     date_pay,
                                                     float(row.get('debet')), row.get('comment'))
                _log_['log'].append({phone: str(com_for_sale.get('communication_id')),
                                     'debet': row.get('debet'), 'data': data_tag_3.get('result').get('data').get('id'),
                                     'updated': False, 'date': com_for_sale.get('start_time')})
        # Все конец!
        return {
            'success': True,
            'message': 'All operations complete!',
            'journal': _log_
        }
    except Exception as e:
        print(elem)
        logging.debug(e, exc_info=True)
        return {
            'success': False,
            'message': 'ERROR: ' + str(e)
        }