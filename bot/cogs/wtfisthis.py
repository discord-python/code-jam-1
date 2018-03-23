#!/usr/bin/env python3.6

import aiohttp
import async_timeout
import asyncio


async def query(params):
    lastcontinue = {}

    async with aiohttp.ClientSession(headers={'User-Agent': 'DickButt v.10rc2'}) as cs:
        async with async_timeout.timeout(20):
            while True:
                req = params.copy()
                req.update(lastcontinue)
                async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                    if 'continue' not in r:
                        break
                    lastcontinue = r['continue']

                    return await r.json()


async def main():
    result = await query({'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links', 'format': 'json'})
    print(result)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())