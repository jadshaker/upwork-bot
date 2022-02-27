import re
from json import load
from datetime import datetime
from functions import fetch_upwork_jobs, to_message
from discord.ext import tasks
from discord.ext.commands import Bot


TOKEN, QUERIES = load(open('config.json')).values()


open('logs.txt', 'w').close()


def log(*values: str) -> None:
    value = f"{datetime.now()} - {' '.join(values)}\n"
    open('logs.txt', 'a').write(value)
    print(value, end='')


bot = Bot('!')

messages = []


async def send_messages(query: str, channel_id: int, per_page: int = 5) -> None:
    channel = bot.get_channel(channel_id)
    fetched_jobs = fetch_upwork_jobs(query=query, per_page=per_page)
    for _ in range(per_page):
        _, job = fetched_jobs.popitem()
        title = re.sub('<[^<]+?>', '', job['title']).strip()
        title = title[:25] + '...' if len(title) > 25 else title
        if query + '-' + title in messages:
            continue
        messages.append(query + '-' + title)
        await channel.send(embed=to_message(job))
        log('sent', title)


@tasks.loop(seconds=30)
async def fetch_data():
    for query in QUERIES:
        await send_messages(*query.values())


@bot.event
async def on_ready():
    log(f'{bot.user} started successfully!\n')
    fetch_data.start()


bot.run(TOKEN)
