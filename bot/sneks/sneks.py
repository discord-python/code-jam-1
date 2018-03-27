import json
import logging
import random
from urllib import parse

import aiohttp

from bs4 import BeautifulSoup

import discord

import requests

# the search URL for the ITIS database
ITIS_BASE_URL = "https://itis.gov/servlet/SingleRpt/{0}"
ITIS_SEARCH_URL = ITIS_BASE_URL.format("SingleRpt")
ITIS_JSON_SERVICE_FULLRECORD = "https://itis.gov/ITISWebService/jsonservice/getFullRecordFromTSN?tsn={0}"
ITIS_JSON_SERVICE_FULLHIERARCHY = "https://itis.gov/ITISWebService/jsonservice/getFullHierarchyFromTSN?tsn={0}"
WIKI_API_URL = "http://en.wikipedia.org/w/api.php?{0}"
WIKI_URL = "http://en.wikipedia.org/wiki/{0}"
IMAGE_SEARCH_URL = "https://api.qwant.com/api/search/images?count=1&offset=1&q={0}+snake"

log = logging.getLogger(__name__)


class Embeddable:
    """
    Represents an object that can be serialized to a :class:`discord.Embed`
    """

    def as_embed(self) -> discord.Embed:
        raise NotImplementedError()


class SnakeDef(Embeddable):
    """
    Represents a snek species
    """

    def __init__(self, common_name="", species="", image_url="", family="", genus="", short_description="",
                 wiki_link="", geo=""):
        self.common_name = common_name
        self.species = species
        self.image_url = image_url
        self.family = family
        self.genus = genus
        self.short_description = short_description
        self.wiki_link = wiki_link
        self.geo = geo

    def as_embed(self):
        # returns a discord embed with the snek
        embed = discord.Embed()
        embed.title = self.species + " (" + self.common_name + ")"
        embed.colour = discord.Colour.green()
        embed.url = self.wiki_link
        if self.family is not None and self.family != "":
            embed.add_field(name="Family", value=self.family)
        if self.genus is not None and self.genus != "":
            embed.add_field(name="Genus", value=self.genus)
        embed.add_field(name="Species", value=self.species)
        embed.set_image(url=self.image_url)
        embed.description = self.short_description
        if len(embed.description) > 1000:
            embed.description = embed.description[:997] + "..."
        if self.geo != "" and self.geo is not None:
            embed.add_field(name="Geography", value=self.geo)
        return embed


class SnakeGroup(Embeddable):

    def __init__(self, common_name="None", scientific_name="None", image_url="", rank="Unknown", sub=[],
                 short_description="A snake group", link="", geo=""):
        self.link = link
        self.common_name = common_name
        self.scientific_name = scientific_name
        self.image_url = image_url
        self.rank = rank
        self.sub = sub
        self.short_description = short_description
        self.geo = geo

    def as_embed(self):
        embed = discord.Embed()
        embed.title = self.scientific_name + (
            (" (" + self.common_name + ")") if self.common_name is not None and self.common_name is not "None" else "")
        embed.description = self.short_description
        if len(embed.description) > 1000:
            embed.description = embed.description[:997] + "..."
        embed.colour = discord.Colour.green()
        embed.url = self.link
        embed.set_image(url=self.image_url)
        if self.common_name is not "None" and self.common_name is not None:
            embed.add_field(name="Common Name", value=self.common_name)
        embed.add_field(name="Taxonomic Rank", value=self.rank)
        if self.geo is not "":
            embed.add_field(name="Geography", value=self.geo)
        return embed


def find_image_url(name: str) -> str:
    """
    Searches an image on the Qwant search engine API
    :param name: the name of the image
    :return: a direct URL to the image, or an empty string if the search was unsuccessful
    """
    req_url = IMAGE_SEARCH_URL.format(name.replace(" ", "+"))
    res = requests.get(url=req_url, headers={"User-Agent": "Mozilla/5.0"})
    if res.status_code != 200:
        return ""
    j = json.JSONDecoder().decode(res.content.decode("utf-8"))
    image_url = j['data']['result']['items'][0]['media']
    return image_url


def is_itis_table_empty(soup) -> bool:
    """
    Checks whether an ITIS search result table is empty
    :param soup: the soup to search in
    :return: true if the search table is empty
    """
    return "No Records Found." in str(soup)


def itis_find_link(soup) -> str:
    """
    Finds the first link in an ITIS search result table
    :param soup: the soup to search in
    :return: a direct URL
    """
    return ITIS_BASE_URL.format(soup.find("a")['href'])


async def wiki_summary(session: aiohttp.ClientSession, name: str, deepcat: str) -> str:
    """
    Finds the summary of the given Wikipedia article
    :param session: the aiohttp HTTP session
    :param name: the title to search
    :param deepcat: (optional) category to search in, recursively
    :return:
    """
    search_url = WIKI_API_URL.format(parse.urlencode({
        'list': 'search',
        'srprop': '',
        'srlimit': 1,
        'srsearch': ("deepcat:" + deepcat + " " + name) if deepcat is not None else name,
        'format': 'json',
        'action': 'query'
    }))
    async with session.get(search_url) as res:
        j = await res.json()
        log.debug(search_url)
        if len(j['query']['search']) is 0:
            return None
        page_title = j['query']['search'][0]['title']
        page_id = str(j['query']['search'][0]['pageid'])
        page_url = WIKI_API_URL.format(parse.urlencode({
            'prop': 'extracts',
            'explaintext': '',
            'titles': page_title,
            'exsentences': '2',
            'format': 'json',
            'action': 'query'
        }))
        async with session.get(page_url) as page_res:
            page_json = await page_res.json()
            return page_json['query']['pages'][page_id]['extract']


async def scrape_itis_page(url: str, initial_query: str) -> Embeddable:
    """
    Scrapes an ITIS page from the direct URL
    :param url: the URL of the ITIS page
    :param initial_query: the initial query submitted in the search
    :return: an Embeddable object to be output
    """
    tsn = parse.parse_qs(parse.urlparse(url).query)['search_value'][0]
    json_url = ITIS_JSON_SERVICE_FULLRECORD.format(tsn)

    async with aiohttp.ClientSession() as session:
        async with session.get(json_url) as res:
            j = await res.text(encoding='iso-8859-1')
            data = json.JSONDecoder().decode(j)
            common_names = []
            for common_name_tag in data['commonNameList']['commonNames']:
                if common_name_tag is None:
                    continue
                if common_name_tag['language'] == "English":
                    common_names.append(common_name_tag['commonName'])
            common_name = ', '.join(common_names)
            rank = data['hierarchyUp']['rankName']
            scientific_name = data['hierarchyUp']['taxonName']
            geo = []
            for geoDivisions in data['geographicDivisionList']['geoDivisions']:
                if geoDivisions is not None:
                    geo.append(geoDivisions['geographicValue'])
            if rank == "Species":
                embeddable = SnakeDef()
                embeddable.common_name = common_name if common_name != "" else "None"
                embeddable.species = data['scientificName']['combinedName']
                embeddable.genus = data['hierarchyUp']['parentName']

                async with session.get(ITIS_JSON_SERVICE_FULLHIERARCHY.format(tsn)) as hierarchy_res:
                    hier_j = await hierarchy_res.text(encoding='iso-8859-1')
                    hier_data = json.JSONDecoder().decode(hier_j)
                    family = "Unknown"
                    for hier in hier_data['hierarchyList']:
                        if hier['rankName'] == 'Family':
                            family = hier['taxonName']
                    embeddable.family = family

                embeddable.image_url = find_image_url(scientific_name)
                embeddable.wiki_link = url
                summary = await wiki_summary(session, scientific_name + " " + initial_query, deepcat='Snake_genera')
                embeddable.short_description = summary if not None else ""
                embeddable.geo = ', '.join(geo)
            else:
                embeddable = SnakeGroup()
                summary = await wiki_summary(session, scientific_name + " " + initial_query, deepcat='Snake_genera')
                embeddable.short_description = summary if not None else ""
                embeddable.common_name = common_name if common_name != "" else "None"
                embeddable.scientific_name = scientific_name
                embeddable.link = url
                embeddable.image_url = find_image_url(scientific_name)
                embeddable.rank = rank
                embeddable.geo = ', '.join(geo)
            return embeddable


async def scrape_itis(name: str) -> Embeddable:
    """
    Searches and scrapes the ITIS database from the given animal name
    :param name: the name of the animal
    :return: an Embeddable object to be output
    """
    form_data = {
        'categories': 'All',
        'Go': 'Search',
        'search_credRating': 'All',
        'search_kingdom': 'Animal',
        'search_span': 'exactly_for',
        'search_topic': 'all',
        'search_value': name,
        'source': 'html'
    }
    res = requests.post(url=ITIS_SEARCH_URL, data=form_data)
    html = res.content.decode('iso-8859-1')
    if "No Records Found?" in html:
        async with aiohttp.ClientSession() as session:
            # no snek, maybe wikipedia?
            snake = SnakeDef()
            snake.short_description = await wiki_summary(session, name, deepcat='Snakes_by_common_name')
            if snake.short_description is None:
                snake.short_description = await wiki_summary(session, name, deepcat='Snake_genera')
                if snake.short_description is None:
                    return None
            snake.species = name.capitalize()
            snake.common_name = snake.species
            snake.wiki_link = WIKI_URL.format(name.capitalize()).replace(' ', '_')
            snake.image_url = find_image_url(name)
            return snake
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table", {"width": "100%"})
    table_common_name = tables[1]
    table_scientific = tables[2]

    is_common_name = not is_itis_table_empty(table_common_name)
    is_scientific = not is_itis_table_empty(table_scientific)

    if not is_common_name and not is_scientific:
        # unknown snek, abort
        return None

    url = None
    if is_scientific:
        url = itis_find_link(table_scientific)
    elif is_common_name:
        url = itis_find_link(table_common_name)
    if url is None:
        return None

    return await scrape_itis_page(url, name)


def snakify(s):
    """
    "Snakifies" a string, by randomly elongating s's and e's
    :param s: the string to "snakify"
    :return: the "snakified" string
    """
    x = random.randint(3, 8)
    y = random.randint(3, 8)
    return s.replace("s", x * "s").replace("e", y * "e") if s is not None else s
