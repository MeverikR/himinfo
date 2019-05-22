import json
import logging
import aiohttp
from aiohttp import ClientSession


class CustomApi():
    url = 'https://himinfo.net/cl/clean_expert/api/?'
#создание seeion_id, пока хз зачем
    async def session(self,login,pwd):
        url = 'https://himinfo.net/cl/clean_expert/api/?Login='
        params = {
            'User': str(login),
            'Pwd': str(pwd),
            'AsUser':'1'
                  }


        param = json.dumps(params)

        async with aiohttp.ClientSession() as session:
            async with session.get(url+param) as resp:
                data = await resp.json()
        return (data)


#получение информации по клиенту
    async def info_client(self,contr_id,session_id):
        url = 'https://himinfo.net/cl/clean_expert/api/?ContrInfoForAll='
        params = {
            'ContrInfoForAll': json.dumps({
                'contr_id': str(contr_id),
            }),
            'SessionID': str(session_id)
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                data = await resp.json()
        return data





#Список заказов за период
    async def ordersbetween(self,StartDate,StopDate,session_id):
        method = 'OrdersBetweenForAll'
        params = {
        'OrdersBetweenForAll':{
        'StartDate': StartDate,
        'StopDate': StopDate,
        },
        'SessionID': session_id
            }
        print(params)

        async with ClientSession() as session:
            response = await session.post(self.url + method, json=params)
            data = await response.json(content_type='text/html')
            return data






