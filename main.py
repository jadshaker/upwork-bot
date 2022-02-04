from SECRETS import DATABASE_URL, TOKEN, MESSAGE_IDS
from datetime import datetime
from functions import fetch_upwork_jobs, to_message
from discord.ext import tasks
from firebase_admin import credentials, initialize_app, db
from discord.ext.commands import Bot


def print(values: str) -> None:
    open('logs.txt', 'a').write(f'{datetime.now()} - {values}\n')


cred = credentials.Certificate('./serviceAccountKey.json')
initialize_app(cred, {'databaseURL': DATABASE_URL})

bot = Bot('!')


@tasks.loop(minutes=1)
async def fetch_data():
    channel = bot.get_channel(939143472055746590)
    old_jobs: dict = db.reference('jobs').get()
    if old_jobs == None:
        old_jobs = []
    fetched_jobs = fetch_upwork_jobs(query='scrap', per_page=5)
    db.reference('jobs').set(fetched_jobs)
    for i in range(5):
        _, job = fetched_jobs.popitem()
        message = await channel.fetch_message(MESSAGE_IDS[i])
        await message.edit(embed=to_message(job))
        print('edited' + str(to_message(job)))


@bot.event
async def on_ready():
    print(f'\n{bot.user} started successfully!')
    fetch_data.start()


bot.run(TOKEN)
