from pyrogram import Client
import configparser
import time
import json
import asyncio

from pyrogram.enums import ChatType


def sender(userListFilepath: str, message: str, delay: int | float, user_tg_id: int) -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    config = configparser.ConfigParser()
    config.read(r'config.ini')

    api_id = config['pyrogram']['api_id']
    api_hash = config['pyrogram']['api_hash']

    with open(userListFilepath, 'r') as file:
        user_ids = [i.replace(' ', '').replace('\n', '') for i in file.readlines()]
    user_succsess_dict = dict()
    client = Client(name='me_client', api_id=api_id, api_hash=api_hash)

    async def sender():
        async with client:
            for ind in range(len(user_ids)):
                user_id = user_ids[ind]
                data_len = len(user_ids)
                chat_data = await client.get_chat(user_id)
                if chat_data.type == ChatType.PRIVATE:
                    await client.send_message(chat_id=user_id, text=message)
                    try:
                        if user_id not in user_succsess_dict:
                            user_succsess_dict[user_id] = 'Успех: отправлено'
                        else:
                            if not isinstance(user_succsess_dict[user_id], list):
                                user_succsess_dict[user_id] = [user_succsess_dict[user_id]]
                            user_succsess_dict[user_id].append('Успех: отправлено')
                    except Exception as e:
                        if user_id not in user_succsess_dict:
                            user_succsess_dict[user_id] = f'Ошибка: {e}'
                        else:
                            if not isinstance(user_succsess_dict[user_id], list):
                                user_succsess_dict[user_id] = [user_succsess_dict[user_id]]
                            user_succsess_dict[user_id].append(f'Ошибка: {e}')
                else:
                    user_succsess_dict[user_id] = 'Ошибка: чат не является приватным'
                if ind < data_len - 1:
                    time.sleep(delay)

        with open(f'отчет_{user_tg_id}.json', 'w') as outfile:
            json.dump(user_succsess_dict, outfile, ensure_ascii=False)

    client.run(sender())
