#!/usr/bin/env python3.6

import aiohttp
import async_timeout
import asyncio


async def wikiquery(params):
    params['format'] = 'json'

    async with aiohttp.ClientSession(headers={'User-Agent': 'DickButt v.10rc2'}) as cs:
        async with async_timeout.timeout(20):
            async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                result = await r.json()

    return result


async def contquery(params):
    last_continue = {}

    while True:
        req = params.copy()
        req.update(last_continue)

        request = await wikiquery(req)

        if 'query' not in request:
            break

        pages = request['query']['pages']['13205433']['links']
        yield pages

        if 'continue' not in request:
            break

        last_continue = request['continue']


async def main():
    ambiguous = ["(disambiguation)", "Wikipedia:", "Help:", "Category:"]
    result = contquery({'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links', 'format': 'json'})
    async for dicks in result:
        listed = dicks
        for item in listed:
            if not any(s in item['title'] for s in ambiguous):
                print(item['title'])

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
