#!/usr/bin/env python3.6

import aiohttp
import async_timeout
import asyncio


async def query(request):
    request['action'] = 'query'
    request['format'] = 'json'
    lastContinue = {}

    async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot'}) as cs:
        while True:
                req = request.copy()
                req.update(lastContinue)
                async with cs.get('https://en.wikipedia.org/w/api.php', params=req) as result:
                    if 'error' in result:
                        raise Error(result['error'])
                    if 'warnings' in result:
                        print(result['warnings'])
                    if 'query' in result:
                        yield result['query']
                    if 'continue' not in result:
                        break
                    lastContinue = result['continue']


result = query({'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links'})

print(result)

async def somebollocks():
    async for item in result:
        print(item)

somebollocks()