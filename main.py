import re
from json import load
from datetime import datetime
from functions import fetch_upwork_jobs, to_message
from discord.ext import tasks
from discord.channel import TextChannel
from discord.ext.commands import Bot


# TODO keep only 'per_page' int of messages in each channel


TOKEN: str
QUERIES: list[dict]
bot: Bot = Bot('!')
messages: list = []
TOKEN, QUERIES = load(open('config.json')).values()

open('logs.txt', 'w').close()


def log(*values: str) -> None:
    value: str = f"{datetime.now()} - {' '.join(values)}\n"
    open('logs.txt', 'a').write(value)
    print(value, end='')


async def send_messages(query: str, channel_id: int, per_page: int = 5) -> None:
    channel: TextChannel = bot.get_channel(channel_id)
    fetched_jobs: dict = fetch_upwork_jobs(query=query, per_page=per_page)
    for _ in range(per_page):
        _, job = fetched_jobs.popitem()
        title: str = re.sub('<[^<]+?>', '', job['title']).strip()
        title = title[:25] + '...' if len(title) > 25 else title
        if query + '-' + title in messages:
            continue
        messages.append(query + '-' + title)
        await channel.send(embed=to_message(job))
        log('sent', title)


@tasks.loop(seconds=30)
async def fetch_data() -> None:
    for query in QUERIES:
        await send_messages(*query.values())


@bot.event
async def on_ready() -> None:
    log(f'{bot.user} started successfully!\n')
    fetch_data.start()


bot.run(TOKEN)
