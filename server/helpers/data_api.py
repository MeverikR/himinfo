from aiohttp import ClientSession



class Dataapi():
    url = 'https://dataapi.comagic.ru/v2.0'
    async def calls(self,token,date_from,date_till):
        params = {
            'jsonrpc': '2.0',
            'id': '1',
            'method': 'get.calls_report',
            'params':
                {
                    'access_token': token,
                    'date_from': date_from,
                    'date_till': date_till,

                    'fields': [
                        'start_time', 'communication_id', 'contact_phone_number', 'talk_duration',
                        'virtual_phone_number', 'tags','sale_date','sale_cost','is_lost'
                    ],
                    'sort': [
                        {
                            'field': 'start_time',
                            'order': 'asc'
                        }
                    ]

                },
        }

        async with ClientSession() as session:
            response = await session.post(self.url, json=params)
            data = await response.json()
            return data



    async def tag_sales(self,method,token,communication_id,date_time,transaction_value,comment=None):
        print('OKAI! I`m tag setter! Setting: [%s] summ [%s]' % (communication_id, transaction_value))
        params = {
              'jsonrpc':'2.0',
              'id':'1',
              'method':method,
                  'params':{
                    'access_token':token,
                    'communication_id':communication_id,
                    'communication_type':'call',
                    'date_time':date_time,
                    'transaction_value':transaction_value,
                    'comment' : str(comment)

                  }
            }
        async with ClientSession() as session:
            response = await session.post(self.url, json=params)
            data = await response.json()
            return data



    async def tag_delete(self,token,communication_id):
        params = {
              'jsonrpc':'2.0',
              'id':'1',
              'method':'unset.tag_communications',
                  'params':{
                    'access_token':token,
                    'communication_id':communication_id,
                    'communication_type':'call',
                    'tag_id':1555
                  }
            }

        async with ClientSession() as session:
            response = await session.post(self.url, json=params)
            data = await response.json()
            return data