import re
from datetime import datetime
from requests import get
from discord import Embed


def fetch_upwork_jobs(query: str, sort: str = 'recency', **kwargs) -> dict:
    """
    # This function fetches jobs from Upwork, according to several parameters
    - query     - Required : text to print (str)
    TODO add sort options
    - sort      - Optional : sort by (str) (default: 'recency')
    - **kwargs  - Optional : other parameters to filter the jobs (dict)
    ---
    # kwargs
    - for parameters of same key with commas in a string
    - for range of values, use '-'
    ---
    # Options
    - client_hires      : range of client hires             | options: 0, 1-9, 10-
    - contractor_tier   : client requested contractor tier  | options: 1 if Entry level, 2 if Intermediate, 3 if Expert
    - duration_v3       : type of duration                  | options: weeks, months, semester, ongoing
    - per_page          : number of jobs per page           | options: custom int, e.g. 10
    - category2_uid     : category id                       | options: custom id, e.g. 531770282584862721
    - workload          : number of hours per week          | options: as_needed (< 30 hours), full_time (> 30 hours)
    - t                 : job type                          | options: 0 if hourly, 1 if fixed
    - covid19_only      : covid19 jobs only                 | options: 1 if covid19 jobs only
    ---
    # Returns
    returns a dictionary of jobs according to given criteria
    """

    req = get(f"https://www.upwork.com/search/jobs/url?q={query}&sort={sort}&{'&'.join(f'{key}={value}' for key, value in kwargs.items())}", headers={
        'X-Requested-With': 'XMLHttpRequest',
        "User-Agent": "Mozilla/5.0",
    })

    return {
        job['ciphertext'][1:]: {
            'title': job['title'],
            'createdOn': job['createdOn'],
            'url': f"https://www.upwork.com/jobs/{job['ciphertext']}",
            'description': job['description'],
            'skills': [skill['prettyName'] for skill in job['skills']],
            'duration': job['duration'],
            'amount': None if job['amount']['amount'] == 0 else f"{job['amount']['amount']} {job['amount']['currencyCode']}",
            'hourlyBudget': job['hourlyBudgetText'],
            'freelancersToHire': job['freelancersToHire'],
            'experience': job['tier'],
            'proposals': job['proposalsTier'],
            'service': job['occupations']['oservice']['prefLabel'],
        } for job in req.json()['searchResults']['jobs']
    }


def to_message(job: dict) -> Embed:
    """
    # This function converts a job to a message
    - job        - Required : job to convert (dict)
    ---
    # Returns
    returns an embedded message of the job
    """

    ENDL = '\n'
    date = job['createdOn']
    year = int(date[:4])
    month = int(date[5:7])
    day = int(date[8:10])
    hour = int(date[11:13])
    minute = int(date[14:16])
    second = int(date[17:19])

    message = Embed(color=0x00ff00)
    description = re.sub(
        '<[^<]+?>', '', f"> {job['description'].strip().replace(ENDL + ENDL, ENDL).replace(ENDL, ENDL + '> ')}\n\n"
    )
    description = description[:200] + \
        '...' if len(description) > 200 else description

    def created_on(seconds: int) -> str:
        if seconds < 60:
            return 'just now'
        elif seconds < 3600:
            return f'{seconds // 60} minute{"s" if seconds >= 120 else ""} ago'
        return f'{seconds // 3600} hour{"s" if seconds >= 7200 else ""} ago'

    message.title = re.sub('<[^<]+?>', '', f":fire: {job['title']}\n\n")
    message.url = job['url']
    message.add_field(
        name=':notepad_spiral: **Description**',
        value=description,
        inline=False
    )
    message.add_field(
        name=f':alarm_clock: Posted',
        value=f'> {created_on((datetime.utcnow() - datetime(year, month, day, hour, minute, second)).seconds)}',
    )
    message.add_field(
        name=':ninja: Skills',
        value=f"> `{'` `'.join(job['skills'])}`\n\n",
        inline=False
    )
    message.add_field(
        name=':calendar: Duration',
        value=f"> {job['duration']}\n\n",
        inline=False
    )
    message.add_field(
        name=f":moneybag: {'Amount' if job['amount'] else 'Hourly Budget'}",
        value=f"> {job['amount'].replace('USD', '$') if job['amount'] else job['hourlyBudget']}\n\n",
        inline=False
    )
    message.add_field(
        name=':briefcase: Freelancers to Hire',
        value=f"> {job['freelancersToHire']}\n\n",
        inline=False
    )
    message.add_field(
        name=':gear: Experience',
        value=f"> {job['experience']}\n\n",
        inline=False
    )

    return message
