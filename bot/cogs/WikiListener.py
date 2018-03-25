import json

import aiohttp

"""

Handle requests and grab and returns detail from wikipedia using MediaWiki.

"""


async def get_json(url):
    """ Returns the text from request to url """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def get_all_snek():
    """" Gets all valid snake from a text file """
    file_save = open("bot/snakedata/common-snake-names.txt", "r")
    snake_text = file_save.read()
    snake_names = snake_text.split("\n")
    print("Returned all snake names")
    return snake_names


async def get_raw_json(name):
    """ Returns a dictionary from the JSON grabbed from MediaWiki API. """
    api_url = f'https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages&exintro=&explaintext=&titles={name}&redirects=1'
    raw_json = await get_json(api_url)
    clean_json = json.loads(raw_json)
    return clean_json


async def get_snek_description(name: str = None):
    """ Returns 'extract' text from JSON, using a dictionary """
    json_dict = await get_raw_json(name)
    return list(json_dict['query']['pages'].values())[0]['extract']


async def get_snek_scientific(name: str = None):
    """ Returns 'title' text from JSON, using a dictionary """
    json_dict = await get_raw_json(name)
    scientific = list(json_dict['query']['pages'].values())[0]['title']
    if scientific == name:
        return None
    else:
        return scientific


async def get_snek_thumbnail(name: str = None):
    """ Returns 'thumbnail' source from JSON, using a dictionary """
    json_dict = await get_raw_json(name)
    return list(json_dict['query']['pages'].values())[0]['thumbnail']['source']


async def get_snek_url(name: str = None):
    """ Returns the url of the snake searched """
    json_dict = await get_raw_json(name)
    title = list(json_dict['query']['pages'].values())[0]['title']
    url = f'https://en.wikipedia.org/wiki/{title}'
    return url
