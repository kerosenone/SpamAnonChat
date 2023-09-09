import asyncio
import os
import time
import socks
from twocaptcha import TwoCaptcha

from telethon.tl.types import KeyboardButton
from telethon.errors import SessionPasswordNeededError
from telethon.sync import TelegramClient, events, connection
from telethon.tl.functions.channels import JoinChannelRequest
from opentele.api import UseCurrentSession
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

with open('./templates/captcha_api.txt', 'r', encoding='utf-8') as file:
    capcha_api = str(file.readline().strip())

solver = TwoCaptcha(capcha_api)

with open('./templates/spam_text.txt', 'r', encoding='utf-8') as file:
    spam_text = str(file.readlines()[0])

with open('./templates/proxy.txt', 'r') as file:
    proxy_data = file.readline().strip()

proxy_parts = proxy_data.split('@')
host_port = proxy_parts[0]
username_password = proxy_parts[1].split(':')

proxy = {
    'host': host_port.split(':')[0],
    'port': int(host_port.split(':')[1]),
    'username': username_password[0],
    'password': username_password[1]
}

sessions = os.listdir('./sessions')
total_messages_sent = 0
total_messages_sent_cp = 0


async def start_bot_dialog(session_path, chat_access_state):
    client = TelegramClient(session_path, proxy=(socks.SOCKS5, proxy['host'], proxy['port'], proxy['username'], proxy['password']))
    await client.connect()
    if not await client.is_user_authorized():
        print(f'{session_path} - невалид')
        return
    else:
        print(f'взял сессию в работу - {session_path}')

    @client.on(events.NewMessage(from_users='@AnonRubot'))
    async def handle_new_message_1(event):
        global total_messages_sent
        if 'Собеседник найден' in event.raw_text:
            await client.send_message('@AnonRubot', spam_text)
            total_messages_sent += 1
            print(f"@AnonRubot - я отправил, ищу следующего {total_messages_sent}")
            await asyncio.sleep(5)
            await client.send_message('@AnonRubot', '/next')
        elif 'Собеседник закончил с вами связь 😞' in event.raw_text:
            await client.send_message('@AnonRubot', '/search')
            print('@AnonRubot - со мной закончили связь, ищу некст')
            await asyncio.sleep(5)
        elif '(от 9 до 99)' in event.raw_text:
            await client.send_message('@AnonRubot', '20')
            await client.send_message('@AnonRubot', '/search')
            print('@AnonRubot - указал возраст 20')
            await asyncio.sleep(5)
        elif 'У вас уже есть собеседник' in event.raw_text:
            print('@AnonRubot - собеседник уже есть, ищу следующего')
            await client.send_message('@AnonRubot', '/next')

        elif 'Чтобы подтвердить, что вы не бот, введите код с картинки' in event.raw_text or \
            'Если вы считаете что вы ни в чём не виноваты, напишите нам: @AnonBotAdmin' in event.raw_text:
            if event.media and event.media.photo:
                image = await event.download_media(file="./downloaded_image.jpg")

                result = solver.normal('downloaded_image.jpg')
                await client.send_message('@AnonRubot', f'{result["code"]}')
                print(f'решил капчу - {result["code"]}, беру след. акк')
                await asyncio.sleep(1)


        elif 'Неправильный код, попробуйте еще, либо пересоздайте капчу' in event.raw_text:
            await client.send_message('c', '/restartcaptcha')
            await asyncio.sleep(3)
            print('рестартанул капчу')

        elif 'Приносим наши извинения, мы временно ограничили вам пользование чатом за нарушение правил Анонимного чата.' in event.raw_text or \
                'У вас ограничение на количество чатов в сутки. Ваши собеседники отправляют жалобы из-за вашего стиля общения' in event.raw_text:
            print('@AnonRubot - аккаунт будет работать потом, щас блок')
            chat_access_state['anon_flag'] = False
            if not chat_access_state['anon_flag'] and not chat_access_state['anon_cp']:
                await client.disconnect()



    @client.on(events.NewMessage(chats='@anonimnyychatbot'))
    async def new_message_handler(event):
        # print(event.raw_text)
        global total_messages_sent_cp
        if 'Шаг 1' in event.raw_text:
            sender = await event.get_sender()
            messages = await client.get_messages(sender.username)
            await messages[0].click(0)
            await client.send_message('@anonimnyychatbot', '/start')
        elif 'Шаг 2' in event.raw_text:
            sender = await event.get_sender()
            messages = await client.get_messages(sender.username)
            print(messages)
            await messages[0].click(0)
            await client.send_message('@anonimnyychatbot', '/start')
        elif 'Шаг 3' in event.raw_text:
            sender = await event.get_sender()
            messages = await client.get_messages(sender.username)
            print(messages)
            await messages[0].click(0)
            await client.send_message('@anonimnyychatbot', '/start')
        elif 'Пожалуйста, выберите желаемую комнату:' in event.raw_text:
            sender = await event.get_sender()
            messages = await client.get_messages(sender.username)
            print(messages)
            await messages[0].click(0)
            await client.send_message('@anonimnyychatbot', '/start')
        elif 'Нашёл кое-кого для тебя!' in event.raw_text:
            await asyncio.sleep(30)
            await client.send_message('@anonimnyychatbot', spam_text)
            total_messages_sent_cp+=1
            print(f"@anonimnyychatbot - я отправил, ищу следующего {total_messages_sent_cp}")
            await asyncio.sleep(5)
            await client.send_message('@anonimnyychatbot', '/next')
        elif 'Диалог остановлен' in event.raw_text:
            await client.send_message('@anonimnyychatbot', '/start')
            print('@anonimnyychatbot - со мной закончили связь, ищу некст')
            await asyncio.sleep(5)
        elif 'Пожалуйста, отправьте нам название вашего населённого пункта' in event.raw_text:
            await client.send_message('@anonimnyychatbot', 'Москва')
            print('@anonimnyychatbot - указал город')
            await asyncio.sleep(5)
            await client.send_message('@anonimnyychatbot', '/start')
            print('@anonimnyychatbot - запустил поиск')
        elif 'Вы уже в очереди или диалоге' in event.raw_text:
            await client.send_message('@anonimnyychatbot', '/next')
            print('@anonimnyychatbot - уже в диалоге, ищу некст')
            await asyncio.sleep(5)
        elif 'Доступ к чату ограничен!' in event.raw_text:
            print(f'@anonimnyychatbot - аккаунт будет работать потом, шас блок')
            chat_access_state['anon_cp'] = False
            if not chat_access_state['anon_flag'] and not chat_access_state['anon_cp']:
                await client.disconnect()
        elif 'Чтобы подтвердить, что вы не робот, введите код с картинки (только крупные символы)' in event.raw_text:
            if event.media and event.media.photo:
                image = await event.download_media(file="./downloaded_image_cp.jpg")
                result = solver.normal('downloaded_image_cp.jpg')
                await client.send_message('@anonimnyychatbot', f'{result["code"]}')
                print(f'@anonimnyychatbot - решил капчу {result["code"]}, беру след. акк')
                await asyncio.sleep(1)
                await client.send_message('@anonimnyychatbot', f'/start')



    async with client:
        try:
            await client.send_message('@anonimnyychatbot', '/start')
            await client.send_message('@AnonRubot', '/start')
            await client.run_until_disconnected()
        except Exception as e:
            print(f'Ошибка бро: {e}')


    print(f'Сессия {session_path} завершена.')

async def check_flags(chat_access_state, event):
    while True:
        if not chat_access_state['anon_flag'] and not chat_access_state['anon_cp']:
            event.set()
            return
        await asyncio.sleep(1)

async def main():
    for session in sessions:
        session_path = os.path.join('./sessions', session)
        chat_access_state = {'anon_flag': True, 'anon_cp': True}
        event = asyncio.Event()

        asyncio.create_task(check_flags(chat_access_state, event))
        await start_bot_dialog(session_path, chat_access_state)
        # await event.wait()

if __name__ == '__main__':
    asyncio.run(main())