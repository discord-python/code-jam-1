async def cont_query(params):
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


async def get_snake_list():
    ambiguous = ["(disambiguation)", "Wikipedia:", "Help:", "Category:"]

    snake_list = []
    result = cont_query({'action': 'query', 'titles': 'list_of_snakes_by_common_name', 'prop': 'links', 'format': 'json'})
    async for dicks in result:
        listed = dicks
        for item in listed:
            if not any(s in item['title'] for s in ambiguous):
                snake_list.append(item['title'])

    return snake_list
