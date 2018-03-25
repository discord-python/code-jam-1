import asyncio

import aiohttp

import json

import ast

import pprint

import re


"""

Handle requests and grab and returns detail from wikipedia using MediaWiki.

"""


async def get_json(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def get_all_snek():
    file_save = open("bot/snakedata/common-snake-names.txt", "r")
    snake_text = file_save.read()
    snake_names = snake_text.split("\n")
    print("Returned all snake names")
    return snake_names


async def get_raw_json(name):
    raw_json = await get_json(f'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages&exintro=&explaintext=&titles={name}&redirects=1')
    return raw_json


async def get_snek_description(name: str = None):
    json_file = await get_raw_json(name)
    clean_json = json.loads(json_file)
    return list(clean_json['query']['pages'].values())[0]['extract']


async def get_snek_scientific(name: str = None):
    json_file = await get_raw_json(name)
    clean_json = json.loads(json_file)
    return list(clean_json['query']['pages'].values())[0]['title']


async def get_snek_thumbnail(name: str = None):
    json_file = await get_raw_json(name)
    clean_json = json.loads(json_file)
    return list(clean_json['query']['pages'].values())[0]['thumbnail']['source']


async def get_snek_url(name: str = None):
    json_file = await get_raw_json(name)
    clean_json = json.loads(json_file)
    title = list(clean_json['query']['pages'].values())[0]['title']
    title.replace(" ", "%20")

    url = f'https://en.wikipedia.org/wiki/{title}'
    return url
    
