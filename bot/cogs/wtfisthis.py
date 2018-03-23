#!/usr/bin/env python3.6

import aiohttp
import async_timeout
import asyncio


async def get_wiki_json(self, params):
    async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot v.10'}) as cs:
        async with async_timeout.timeout(20):
            async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                return await r.json()


async def query(params):
    async with aiohttp.ClientSession(headers={'User-Agent': 'DickButt v.10rc2'}) as cs:
        async with async_timeout.timeout(20):
            async with cs.get("https://en.wikipedia.org/w/api.php", params=params) as r:
                return await r.json()
    # request['action'] = 'query'
    # request['format'] = 'json'
    # lastContinue = {}
    #
    # async with aiohttp.ClientSession(headers={'User-Agent': 'DevBot'}) as cs:
    #     while True:
    #             req = request.copy()
    #             req.update(lastContinue)
    #             async with cs.get('https://en.wikipedia.org/w/api.php', params=req) as result:
    #                 if 'error' in result:
    #                     raise Error(result['error'])
    #                 if 'warnings' in result:
    #                     print(result['warnings'])
    #                 if 'query' in result:
    #                     yield result['query']
    #                 if 'continue' not in result:
    #                     break
    #                 lastContinue = result['continue']


result = query({'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links'})

print(result)
