# a tool to fetch some sneks
# should be run in the same pipenv as the bot (using pipenv shell)

import asyncio
import pickle

import aiohttp

OUTPUT_FILE = "sneks.pickle"
FETCH_URL = "https://en.wikipedia.org/w/api.php?action=query&list=categorymembers" \
            "&cmtitle=Category:Snake_genera&cmlimit=500&cmtype=page&format=json"


async def fetch(session):
    async with session.get(FETCH_URL) as res:
        return await res.json()


loop = asyncio.get_event_loop()

with aiohttp.ClientSession(loop=loop) as session:
    result = loop.run_until_complete(
        fetch(session)
    )
    snake_names = [r['title'] for r in result['query']['categorymembers']]
    with open(OUTPUT_FILE, 'wb') as out:
        pickle.dump(snake_names, out)
        print('done output of ' + str(len(snake_names)) + ' sneks')

loop.close()
