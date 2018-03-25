from mediawiki import MediaWiki
import random
wikipedia = MediaWiki()

snake_list = [link.lower() for link in wikipedia.page('List_of_snakes_by_common_name').links]

def get_snek(snek):
    snek_list = list_sneks(snek)
    for snek in snek_list:
        if snek.lower() in snake_list:
            return snek

def get_snek_page(snek):
    page = wikipedia.page(snek)
    return page

def get_info(page):
    info = {
        'title' : page.title,
        'summary' : page.summary,
        'image' : page.images[0]
    }

    return info

def random_snek():
    snek = random.choice(snake_list)
    return snek

def suggestions(snek):
    snek_list = list_sneks(snek)
    for snek in snek_list:
        if snek in snake_list:
            return snek

def list_sneks(snek):
    return wikipedia.prefixsearch(snek, results = 10)
    
choice = input("snake: ")
try:
    snek = get_snek(choice)
    page = get_snek_page(snek)
    print(get_info(page))
except:
    if choice not in snake_list:
        print("this is not a snake")
    else:
        print("sorry, we couldn't find that snake, here are some suggestions:\n")
        suggestions(choice)