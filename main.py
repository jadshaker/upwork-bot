from SECRETS import TOKEN, MESSAGE_IDS
from datetime import datetime
from functions import fetch_upwork_jobs, to_message
from discord.ext import tasks
from discord.ext.commands import Bot


def log(*values: str, start='') -> None:
    open('logs.txt', 'a').write(
        f"{start}{datetime.now()} - {' '.join(values)}\n"
    )


bot = Bot('!')


@tasks.loop(minutes=1)
async def fetch_data():
    channel = bot.get_channel(939143472055746590)
    fetched_jobs = fetch_upwork_jobs(query='scrap', per_page=5)
    for i in range(5):
        _, job = fetched_jobs.popitem()
        message = await channel.fetch_message(MESSAGE_IDS[i])
        await message.edit(embed=to_message(job))
        log('edited', str(to_message(job)))


@bot.event
async def on_ready():
    log(f'{bot.user} started successfully!\n', start='\n\n')
    fetch_data.start()


bot.run(TOKEN)
