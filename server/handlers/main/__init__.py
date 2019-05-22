import logging
from aiohttp import web
from helpers.config import Config
from helpers.agbis_api import CustomApi
from helpers.data_api import Dataapi
from helpers.models.data import Data
from helpers.db import get_one_row, get_insert_row,get_apdate
from .api import api
from datetime import datetime, timedelta
from pprint import pprint
import urllib.parse

config = Config.get_config()
CustomApi = CustomApi()
Dataapi = Dataapi()

logger = logging.getLogger('agbis')


async def Main(self):
    try:
        StopDate = datetime.now().strftime("%d.%m.%Y")
        StartDate = (datetime.now() + timedelta(days=-1)).strftime("%d.%m.%Y")
        db = self.app.get('db')

        auth = await CustomApi.session(**config['api'])

        if auth.get('error') != 0:
            print('dropped by authorization')
        else:
            request_api = await CustomApi.ordersbetween(StartDate, StopDate, auth['Session_id'])

            if request_api.get('error') != 0:
                print('dropped by data request')
            else:
                for client_phone in request_api['orders']:
                    client_phone['phone'] = await CustomApi.info_client(client_phone['contr_id'], auth['Session_id'])
                    inserter = {}
                    inserter['contr_id'] = client_phone.get('contr_id')
                    inserter['fone_cell'] = urllib.parse.unquote(client_phone.get('phone').get('fone_cell'))[1:]
                    summ = 0
                    if 'payments' in client_phone:
                        if client_phone.get('payments') is not None and len(client_phone.get('payments')) > 0 :
                            inserter['date_pay'] = datetime.strptime(client_phone.get('payments')[0].get('date_pay'),
                                                                     '%d.%m.%Y+%H:%M:%S')
                            for x in client_phone.get('payments'):
                                summ += float(x.get('debet').replace(',', '.'))

                            inserter['debet'] = str(summ)
                        else:
                            print('Payments exists but no first element found')
                    else:
                        print('No payments found')

                    if inserter.get('debet') is not None \
                            and inserter.get('fone_cell') is not None\
                            and inserter.get('fone_cell').strip() != '':
                        pprint(inserter)
                        phone_exists = await get_one_row(Data.check_phone(inserter.get('fone_cell')), db)
                        if phone_exists is not None:
                            phone_exists = dict(phone_exists)
                            if len(phone_exists) >0:
                                cur_debet = float(inserter['debet']) + float(phone_exists.get('debet', 0))
                                updater = {}
                                updater['debet'] =  str(cur_debet)
                                db_pdate = await get_apdate(Data.update(updater,inserter.get('fone_cell')), db)

                        else:
                            db_data = await get_insert_row(Data.get_insert(inserter), db)
            #send tags
            await api(db)





            return web.json_response({'Data': 1})

    except Exception as e:
        logging.debug(str(e))
        raise web.HTTPClientError(body=str(e))
