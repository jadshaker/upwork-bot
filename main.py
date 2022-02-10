import re
from SECRETS import TOKEN, IDS
from datetime import datetime
from functions import fetch_upwork_jobs, to_message
from discord.ext import tasks
from discord.ext.commands import Bot


def log(*values: str) -> None:
    value = f"{datetime.now()} - {' '.join(values)}\n"
    open('logs.txt', 'a').write(value)
    print(value, end='')


bot = Bot('!')


async def send_messages(channel_id: int, query: str, message_ids: list, per_page: int = 5):
    channel = bot.get_channel(channel_id)
    fetched_jobs = fetch_upwork_jobs(query=query, per_page=per_page)
    for i in range(per_page):
        _, job = fetched_jobs.popitem()
        title = re.sub('<[^<]+?>', '', job['title']).strip()
        title = title[:25] + '...' if len(title) > 25 else title
        try:
            message = await channel.fetch_message(message_ids[i])
            await message.edit(embed=to_message(job))
            log('edited', title)
        except:
            await channel.send(embed=to_message(job))
            log('sent', title)


@tasks.loop(minutes=1)
async def fetch_data():
    await send_messages(
        IDS['scrap']['channel_id'], 'scrap', IDS['scrap']['message_ids'], per_page=5
    )
    await send_messages(
        IDS['python']['channel_id'], 'python', IDS['python']['message_ids'], per_page=5
    )
    await send_messages(
        IDS['machine-learning']['channel_id'], 'machine-learning', IDS['machine-learning']['message_ids'], per_page=5
    )


@bot.event
async def on_ready():
    log(f'{bot.user} started successfully!\n')
    fetch_data.start()


bot.run(TOKEN)
