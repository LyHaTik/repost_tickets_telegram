import os
import signal
import asyncio
from datetime import datetime

from telethon import TelegramClient, events
from dotenv import load_dotenv


load_dotenv()

api_id = int(os.getenv('API_TG_ID'))
api_hash = os.getenv('API_TG_HASH')
phone_number = os.getenv('PHONE_NUMBER')
your_tg_group_id = int(os.getenv('YOUR_TG_GROUP_ID'))

session_name = f'my_tg_session_{api_id}'
system_version = "Windows 10"
listen_groups = [
    -1001846854055,   # Билеты в Таиланд и Вьетнам
    -1001043585622,   # TravelRadar — дешевые авиабилеты, туры, путешествия
    -1001797015266,   # KJA Авиабилеты Красноярск
    -1001395771813,   # IKT Билеты Иркутск
    -1001826008316,   # БИЛЕТЫ: Юг и Кавказ | Сочи, МинВоды, Махачкала, Владикавказ, Ставрополь
    -1001946693397,   # БИЛЕТЫ: Урал | Екатеринбург, Пермь, Тюмень, Челябинск
    -1001647814009,   # БИЛЕТЫ: Москва и СПб
    -1001260864774,   # Билеты из Сибири - Новосибирск, Томск, Омск, Кузбасс, Алтай, Красноярск, Иркутск
    -1001974549803,   # БИЛЕТЫ: Дальний Восток
    -1001804546948,   # LED Билеты Санкт-Петербург
    -1001890360120,   # KZN Билеты Казань
    ]            

client = TelegramClient(
    session_name,
    api_id,
    api_hash,
    system_version=system_version
    )

shutdown_event = asyncio.Event()

@client.on(events.NewMessage(chats=listen_groups))
async def forward_messages(event):
    try:
        await client.send_message(your_tg_group_id, event.message)
        print(f'{datetime.now()} INFO: OK! FORWARD MESSAGE.', flush=True)
    except Exception as e:
        print(f'{datetime.now()} ERROR: {e}', flush=True)


async def main():
    await client.start(phone_number)
    print(f'{datetime.now()} INFO: Bot started and listening...', flush=True)
    
    await shutdown_event.wait()
    
    print(f'{datetime.now()} INFO: Bot stopped.', flush=True)
    await client.run_until_disconnected()

def handle_shutdown(signum):
    print(f'{datetime.now()} INFO: Received shutdown signal ({signum}).', flush=True)
    shutdown_event.set()


# Подписываемся на системные сигналы
signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

    