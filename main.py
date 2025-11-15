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
    if not event.message:
        # Сообщение пустое или сервисное — пропускаем
        return
    try:
        # Проверяем, является ли сообщение частью альбома
        if event.message.grouped_id:
            # Получаем все сообщения с этим grouped_id (в альбоме)
            messages = await client.get_messages(
                entity=event.chat_id,
                ids=range(event.message.id - 9, event.message.id + 1)  # Берём последние 10 сообщений
            )
            media_group = [m for m in messages if m.grouped_id == event.message.grouped_id]

            for i, m in enumerate(media_group):
                caption = m.text if i == 0 else None  # подпись только к первому медиа
                if caption and len(caption) > 1024:
                    long_caption = caption
                    caption = None  # убираем подпись, текст отправим отдельно
                else:
                    long_caption = None

                if m.media:
                    await client.send_file(
                        your_tg_group_id,
                        file=m.media,
                        caption=caption
                    )
                    print(f'{datetime.now()} INFO: OK! FORWARD MESSAGE MEDIA.', flush=True)

                # Если подпись была слишком длинная — отправляем отдельно
                if long_caption:
                    await client.send_message(your_tg_group_id, long_caption)
                    print(f'{datetime.now()} INFO: OK! FORWARD long_caption.', flush=True)

        # Если просто медиа (не альбом)
        elif event.message.media:
            caption = event.message.text
            if caption and len(caption) > 1024:
                long_caption = caption
                caption = None
            else:
                long_caption = None

            await client.send_file(
                your_tg_group_id,
                file=event.message.media,
                caption=caption
            )
            print(f'{datetime.now()} INFO: OK! FORWARD MESSAGE MEDIA.', flush=True)

            if long_caption:
                await client.send_message(your_tg_group_id, long_caption)
                print(f'{datetime.now()} INFO: OK! FORWARD long_caption.', flush=True)

        # Если просто текст
        else:
            if event.message.text:
                await client.send_message(your_tg_group_id, event.message.text)
                print(f'{datetime.now()} INFO: OK! FORWARD MESSAGE.', flush=True)

    except Exception as e:
        print(f'{datetime.now()} ERROR: {e}\n MESSAGE: {event.message}', flush=True)




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

    