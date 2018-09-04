import datetime
import time
import eventlet
import logging
import requests
import os
import random
import asyncio
import aiohttp
import json
from discord import Game, Client
from discord.ext.commands import Bot

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# контакт, токен
TOKEN_VK = 'bdd5847d567892bd744fc2865f54381d4ae7b5494a6e3ab93b996a17c8f54620d2ff6af36a50c1daa5c29'
FILENAME_VK = os.path.join(THIS_FOLDER, 'last_known_id.txt')
URL_VK = 'https://api.vk.com/method/wall.get?domain=podcastogru&count=5&filter=owner&access_token={0}&v=5.60'.\
    format(TOKEN_VK)
BASE_POST_VK_URL = 'https://vk.com/wall-115220159_'  # все записи вввввв

# ютуб, токен
TOKEN_YOUTUBE = 'AIzaSyAbxnp4LAowTIMDJaY5-Bc_4PLfihVGIj4'
FILENAME_YOUTUBE = os.path.join(THIS_FOLDER, 'last_update.txt')
URL_YOUTUBE = 'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=UUjL57vLdE5Ae1frLxevzHaw&key={0}' \
            '&part=snippet&maxResults=5'.format(TOKEN_YOUTUBE)
BASE_POST_YOUTUBE_URL = 'https://www.youtube.com/watch?v='


DISCORD_TOKEN = 'NDY2NjkxMDE5NDA1MDAwNzE0.DifxFA.X0VMF5j8Du6ilbSBSbSvjVBDCY8'   # 'NDQ1Mjk0MDY1NjMwNzA3NzYy.DdoYLg.jn2CM30ebDAUTtlcep-kinpukl4'
CHANNEL_NAME = '201418427091386368'
BOT_PREFIX = ("!",)
client = Bot(command_prefix=BOT_PREFIX)


async def get_data():   # функция для получения данных с ресурса
    async with aiohttp.ClientSession() as session:
        # raw_feed = await session.get(URL_VK)
        raw_feed = await session.get(URL_YOUTUBE)
        feed = await raw_feed.text()
        feed = json.loads(feed)
        return feed


@client.event   # функция для отправки сообщения в дискорд
async def send_new_posts(items, last_update):
    channel = client.get_channel(CHANNEL_NAME)
    for i in range(len(items)-1, -1, -1):
        # if item['id'] <= last_id:
        if items[i]['snippet']['publishedAt'] <= last_update:
            continue
        # link = '{!s}{!s}'.format(BASE_POST_VK_URL, item['id'])
        link = '{!s}{!s}'.format(BASE_POST_YOUTUBE_URL, items[i]['snippet']['resourceId']['videoId'])
        await client.send_message(channel, link)
        new_update = items[i]['snippet']['publishedAt']
        print(channel, link, '  ', new_update)
        break
    return new_update


async def check_new_video():    # функция-сборка по поиску, отправки сообщение в дискорд
    await client.wait_until_ready()
    while not client.is_closed:
        with open(FILENAME_YOUTUBE, 'rt') as file:
            last_update = str(file.read())
            if last_update is None:
                logging.error('Could not read from storage. Skipped iteration.')
                return
            logging.error('Last update = {!s}'.format(last_update))
        try:
            feed = await get_data()
            if feed is not None:
                entries = feed['items']
                new_update = await send_new_posts(entries, last_update)
                with open(FILENAME_YOUTUBE, 'wt') as file:
                    file.write(new_update)
                    logging.error('New date update is {!s}'.format(new_update))

        except Exception as ex:
            logging.error('Exception of type {!s} in check_new_video(): {!s}'.format(type(ex).__name__, str(ex)))
            pass
        logging.info('Finished scanning')
        logging.info('[App] Script went to sleep.')
        await asyncio.sleep(3600)


@client.command(pass_context=True)
async def about(context):
    channel = client.get_channel('445292904127266828')  # для метода say значение channel не нужен
    msg = 'Приветствую, {0.author.mention}. Я, {1.user.name}, буду рассказывать вам о новых видео своего тезки. ' \
          'Надеюсь, в будущем я стану полезнее '.format(context.message, client)
    await client.say(msg)


@client.event   # установка свойства играет с кем-то
async def on_ready():
    await client.change_presence(game=Game(name="Быть человеком"))
    print("Logged in as " + client.user.name)
    print(client.user.id)
    print('------')


if __name__ == '__main__':

    logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s', level=logging.INFO,
                        filename=os.path.join(THIS_FOLDER, 'bot_log.log'), datefmt='%d.%m.%Y %H:%M:%S')
    now_day = datetime.datetime.now()
    if not os.path.exists(FILENAME_YOUTUBE):
        with open(FILENAME_YOUTUBE, 'wt') as file:
            file.write(now_day.isoformat())
            logging.error('Start date is {!s}'.format(now_day.isoformat()))

    client.loop.create_task(check_new_video())
    client.run(DISCORD_TOKEN)
