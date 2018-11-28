import datetime
import time
import eventlet
import logging
import os
import asyncio
import aiohttp
import json
from discord import Game, Embed
from discord.ext.commands import Bot
from vk_url_parser import url_parser
import config


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
FILENAME_VK = os.path.join(THIS_FOLDER, 'last_known_id.txt')
#  URL_VK = 'https://api.vk.com/method/wall.getById?posts={1}&extended=1&copy_history_depth=2' \
#         '&access_token={0}&v=5.60'.format(token_list['TOKEN_VK'], list1)
BASE_POST_VK_URL = 'https://vk.com/wall-115220159_'  # все записи вввввв

# ютуб, токен

FILENAME_YOUTUBE = os.path.join(THIS_FOLDER, 'last_update.txt')
BASE_POST_YOUTUBE_URL = 'https://www.youtube.com/watch?v='


CHANNEL_NAME = '201418427091386368'
BOT_PREFIX = ("!",)
client = Bot(command_prefix=BOT_PREFIX)


async def get_data(url):   # функция для получения данных с ресурса, работает
    async with aiohttp.ClientSession() as session:
        # raw_feed = await session.get(URL_VK)
        raw_feed = await session.get(url)
        feed = await raw_feed.text()
        feed = json.loads(feed)
        return feed


@client.event   # функция для отправки сообщения в дискорд
async def send_new_posts(items, last_update):
    channel = client.get_channel(CHANNEL_NAME)
    for i in range(len(items)-1, -1, -1):
        # if item['id'] <= last_id:
        if items[i]['snippet']['publishedAt'] <= last_update:
            print(items[i]['snippet']['publishedAt'])
            continue
        # link = '{!s}{!s}'.format(BASE_POST_VK_URL, item['id'])
        link = '{!s}{!s}'.format(BASE_POST_YOUTUBE_URL, items[i]['snippet']['resourceId']['videoId'])
        await client.send_message(channel, link)
        new_update = items[i]['snippet']['publishedAt']
        print(channel, link, '  ', new_update)
        return new_update  # break раньше здесь был брейк


async def check_new_video():    # функция-сборка по поиску, отправки сообщение в дискорд
    URL_YOUTUBE = 'https://www.googleapis.com/youtube/v3/playlistItems?playlistId=UUjL57vLdE5Ae1frLxevzHaw&key={0}' \
                  '&part=snippet&maxResults=5'.format(token_list['TOKEN_YOUTUBE'])
    await client.wait_until_ready()
    while not client.is_closed:
        with open(FILENAME_YOUTUBE, 'rt') as file1:
            last_update = str(file1.read())
            if last_update is None:
                logging.error('Could not read from storage. Skipped iteration.')
                return
            logging.error('Last update = {!s}'.format(last_update))
        try:
            feed = await get_data(URL_YOUTUBE)
            if feed is not None:
                entries = feed['items']
                new_update = await send_new_posts(entries, last_update)
                if new_update:
                    with open(FILENAME_YOUTUBE, 'wt') as file2:
                        file2.write(new_update)
                        logging.error('New date update is {!s}'.format(new_update))

        except Exception as ex:
            logging.error('Exception of type {!s} in check_new_video(): {!s}'.format(type(ex).__name__, str(ex)))
            pass
        logging.info('Finished scanning')
        logging.info('[App] Script went to sleep.')
        await asyncio.sleep(3600)


@client.listen('on_message')
async def vk_message(message):
    url_list = url_parser(message.content)
    if url_list:
        for ByID in url_list:
            URL_VK = 'https://api.vk.com/method/wall.getById?posts={1}&extended=1&copy_history_depth=2' \
                     '&access_token={0}&v=5.92'.format(token_list['TOKEN_VK'], ByID)
            wall = await get_data(URL_VK)
            if wall is not None:
                text = wall['response']['items'][0]['text']
                try:
                    author = 'by {0[first_name]} {0[last_name]} '.format(wall['response']['profiles'][0])
                except KeyError:
                    print ('Была срань')
                    author = 'by owner '
                finally:
                    group = 'in {}'.format(wall['response']['groups'][0]['name'])
                em = Embed(description=text, colour=0x4A76A8)
                em.set_author(name='ВК вещает')
                em.set_footer(text='{!s}{!s}'.format(author, group))
                await client.send_message(message.channel, embed=em)


@client.command(pass_context=True)
async def about(context):
    msg = 'Приветствую, {0.author.mention}. Я, {1.user.name}, буду делать всякое, и, надеюсь, меня не взломают, как ' \
          'предшественника.'.format(context.message, client)
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
    token_list = config.check_config()
    client.loop.create_task(check_new_video())
    client.run(token_list['DISCORD_TOKEN'])
