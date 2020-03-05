"""
Lots of websites disagree on what the top 100 movies of all time are, so I wanted to find out
what they actually are.

This scrapes a few different websites (I plan on adding more) and gets their top 100 list,
compiles all lists into one big list, and counts how often a movie appears in the list.

AUTHOR: Preston Carlton
DATE CREATED: Feb 28, 2020
"""
import os
import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from imdb import IMDb
from string import capwords
import json
import collections.abc

# all urls
imdb_url = "https://www.imdb.com/list/ls055592025/?mode=simple"
hwood_reporter_url = "https://www.hollywoodreporter.com/lists/100-best-films-ever-hollywood-favorites-818512"
empire_url = "https://www.empireonline.com/movies/features/best-movies-2/"
rt_url = "https://www.rottentomatoes.com/top/bestofrt/"
wiki_gross_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
afi_url = "https://www.afi.com/afis-100-years-100-movies/"
timeout_url = "https://www.timeout.com/newyork/movies/best-movies-of-all-time"
timeout_actors_url = "https://www.timeout.com/newyork/movies/100-best-movies-as-chosen-by-actors"
binsider_url = "https://www.businessinsider.com/50-best-movies-all-time-critics-2016-10"
ranker_url = "https://www.ranker.com/crowdranked-list/the-best-movies-of-all-time"
goodmovies_url = "https://goodmovieslist.com/best-movies/best-250-movies.html"

# lists to contain all movie titles
imdb_list = []
hwood_reporter_list = []
empire_list = []
rt_list = []
wiki_gross_list = []
afi_list = []
timeout_list = []
timeout_actors_list = []
binsider_list = []
ranker_list = []
goodmovies_list = []

# illegal chars list for filenames
illegal_chars = [
    '!',
    ',',
    '-',
    '&',
    '?',
    '/',
    '\\',
    "'",
    ':',
    '.',
    '—',
    '·'
]

# nary to contain all the information about the movies
master_list = {}



def update(orig, new):
    '''
    helper function to assist in updating nested dictionaries
    '''
    for k, v in new.items():
        if isinstance(v, collections.abc.Mapping):
            orig[k] = update(orig.get(k, {}), v)
        else:
            orig[k] = v
    return orig


def update_movie_data(data):
    '''
    updates the movie's datafile with given 'nary
    data is formatted like so:
    {
        "The Godfather (1972)": {
            "ranks":{
                "imdb":1,
                "empire":2
            }
            "ratings":{
                "imdb":{
                    "score":9.3,
                    "reviews":13
                },
                "rotten_tomatoes":{
                    "score":10,
                    "reviews":10365
                }
            },
            "gross":248000000

        }
    }

    '''
    # get the filename of the movie
    movie_title = list(data.keys())[0]
    # remove all bad chars
    filename = movie_title.translate({ord(c): None for c in illegal_chars})
    # replace all the double spaces
    filename = filename.replace('  ', ' ')
    filename = filename.replace(' ', '_')
    filename = filename.lower() + '.json'

    if not os.path.exists(f'data/movies/{filename}'):
        # if the movie doesn't already have a datafile, we can create one now
        with open(f'data/movies/{filename}', 'w') as movie_file:
            movie_file.write(json.dumps(data))
        # exit the func so nothing else happens
        return
    # if it does exist, we need to update the 'nary
    with open(f'data/movies/{filename}', 'r') as movie_file:
        stored_data = movie_file.read()
    # load it into a json 'nary

    stored_data = json.loads(stored_data)
    # here we need to access the first item in the 'nary rather than
    # just overwriting the whole thing. this way, we can account for naming
    # discrepancies

    update(stored_data,data)
    # finally, save the newly-updated data to the datafile
    with open(f'data/movies/{filename}', 'w') as movie_file:
        movie_file.write(json.dumps(stored_data))


def parse_imdb():
    '''
    parse the imdb_url and save movie titles to imdb_list
    '''
    page = urlopen(imdb_url)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # find the list elem ('.lister-list')
    list_items = soup.find('div', attrs={
                           'class', 'lister-list'}).find_all('div', attrs={'class', 'lister-item'})
    # loop thru all items in the list
    for item in list_items:
        # get the wrapper of the content data
        content = item.find('div', attrs={
                            'class', 'lister-item-content'}).find('div', attrs={'class', 'lister-col-wrapper'})
        # access the div that contains the title
        header_div = content.find(
            'div', attrs={'class', 'col-title'}).find('span')
        # access the div that contains the movie's IMDB rating
        rating_div = content.select_one('.col-imdb-rating')
        movie_rating = rating_div.text.strip()
        # convert rating into a float
        movie_rating = float(movie_rating)
        # access the number of ratings
        num_reviews = rating_div.select_one('strong')['title']
        # at this point, num_reviews is formatted like this:
        # 9.2 base on 1,512,511 votes
        # we need to extract the 1,512,511
        num_reviews = num_reviews.replace(str(movie_rating),'')

        # base on 1,512,511
        num_reviews = re.findall(r'(?:^|\s)(\d*\.?\d+|\d{1,3}(?:,\d{3})*(?:\.\d+)?)(?!\S)',num_reviews)[0]
        num_reviews = int(num_reviews.replace(',',''))

        # get all parts in the header_div
        header_elems = header_div.find_all('span')
        # access the movies rank in the list, convert to int, and strip the trailing .
        movie_index = int(header_elems[0].text.strip('.'))
        # finally, get the movie's title (just kidding, this is ANOTHER WRAPPER)
        title_div = header_elems[1]
        # there's two elements in this; the movie's title and the year it was released. we want both.
        movie_title = title_div.find('a').text.strip()
        # get movie year
        movie_year = title_div.find('span').text.strip()
        # add year to the movie title
        display_title = ' '.join([movie_title, movie_year])
        # construct moviedata
        movie_data = {
            display_title: {
                'ranks': {
                    'imdb': movie_index
                },
                'ratings': {
                    'imdb': {
                        'score': movie_rating,
                        'reviews': num_reviews
                }
            }
        }
        }
        # update the movie data
        update_movie_data(movie_data)
        # FINALLY, add the movie to the imdb_list
        imdb_list.append(display_title)


def parse_hwood_reporter():
    '''
    parse the hollywood reporter url and save movie titles to hwood_reporter_list
    '''
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(hwood_reporter_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # find the list elem ol.list--ordered__items
    list_items = soup.find('ol').find_all('li')
    # loop thru all items in the list
    for item in list_items:
        # get the bodygroup (not used yet)
        body_div = item.find('div')

        # get the headergroup
        header_div = item.find('header')
        # grab the movie's rank
        movie_index = header_div.select_one('.list-item__index').text
        movie_index = int(movie_index)
        # the only h1 in this div is the title
        movie_title = header_div.find('h1').text.strip()
        # the only h2 is the year
        movie_year = header_div.find('h2').text.strip()
        # combine year + title to get the full name
        display_title = ' '.join([movie_title, movie_year])
        # construct moviedata
        movie_data = {
            display_title: {
                'ranks': {
                    'hollywood_reporter': int(movie_index)
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        hwood_reporter_list.append(display_title)


def parse_empire():
    '''
    parse the empire url and save movie titles to empire_list
    '''
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(empire_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # by far the most poorly organized page.
    container = soup.find('div', attrs={'class', 'article__content'})
    # everything is just on the same level
    title_divs = container.find_all('h2')
    for item in title_divs:
        # parse text from the item
        text = item.text
        # no organization at all!! so we have to split by a . and then re-join the content
        movie_index = text.split('.')[0]
        movie_title = '.'.join(text.split('.')[1:]).strip()
        # parse movie year from movie_title
        movie_year = movie_title.split(' ')[-1].strip()
        # remove movie year from movie_title
        movie_title = movie_title.strip(movie_year).strip()
        # yes, i realize that i just removed the year from the title. later on, this will (probably) be useful.
        display_title = ' '.join([movie_title, movie_year])
        # construct moviedata
        movie_data = {
            display_title: {
                'ranks': {
                    'empire': int(movie_index)
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        empire_list.append(display_title)


def parse_tomatoes():
    '''
    parse the rotten tomatoes url and save movie titles to rt_list
    '''
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(rt_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # nice! the whole list is just in a table!
    table = soup.find('table', attrs={'class': 'table'})
    table_rows = table.find_all('tr')
    for item in table_rows:
        # each row is split into 4 parts; the index, rating, title, and # of ratings
        row_parts = item.find_all('td')
        # if the row has less than 4 items, it's not part of the movie list so we should ignore it
        if len(row_parts) < 4:
            continue
        # grab the index
        movie_index = row_parts[0].text.strip('.')
        # we need to convert this from a percentage to a decimal
        movie_rating = row_parts[1].text.strip().replace('%','')
        movie_rating = int(movie_rating)/10
        # this is already formatted how we want to display it
        display_title = row_parts[2].text.strip()
        num_reviews = int(row_parts[3].text)
        # movie_title contains the year in the title, so we need to split that up
        movie_year = display_title.split(' ')[-1].strip()
        movie_title = display_title.strip(movie_year)
        # construct moviedata
        movie_data = {
            display_title: {
                'ranks': {
                    'rotten_tomatoes': int(movie_index)
                },
                'ratings': {
                    'rotten_tomatoes': {
                        'score': movie_rating,
                        'reviews': num_reviews
                    }
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        rt_list.append(display_title)


def parse_wiki_gross():
    '''
    parse the wiki top grossing films url and save movie titles to wiki_gross_list
    '''
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(wiki_gross_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # nice! the whole list is just in a table!
    # table = soup.find('table', attrs={'class': 'wikitable sortable'})
    table = soup.select_one('table.wikitable.sortable')
    table_rows = table.find_all('tr')
    for item in table_rows:
        # if the first th is "Rank", this is the header row
        if item.find('th').text.strip() == "Rank":
            continue
        # split that bad boi up into cells
        row_parts = item.find_all('td')
        movie_index = row_parts[0].text.strip()
        movie_title = item.find('th').text.strip()
        movie_year = row_parts[3].text.strip()
        display_title = ' '.join([movie_title, f'({movie_year})'])

        wiki_gross_list.append(capwords(display_title))


def parse_afi():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(afi_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select('label.container > h6.q_title')
    for item in list_items:
        # the title is formatted as such: "1. CITIZEN KANE (1941)" so we have to parse it
        movie_index = item.text.split('.')[0]
        movie_title = '.'.join(item.text.split('.')[1:]).strip()
        # currently, i feel like the title is yelling at me. that makes me uncomfortable
        movie_title = capwords(movie_title)
        movie_data = {
            movie_title: {
                'ranks': {
                    'afi': int(movie_index)
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        afi_list.append(capwords(movie_title))


def parse_timeout():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(timeout_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select(
        '#content > article > div > div > div > div > div > article > div.card-content > header > h3 > a')

    for index, item in enumerate(list_items[:-1]):
        movie_title = item.text.strip()
        movie_data = {
            movie_title: {
                'ranks': {
                    'timeout': index+1
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        # add that bad boi to the list
        timeout_list.append(capwords(movie_title))


def parse_timeout_actors():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(timeout_actors_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select(
        '#content > article > div > div > div > div > div > article > div.card-content > header > h3 > a')

    for index, item in enumerate(list_items[:-1]):
        movie_title = item.text.strip()
        movie_data = {
            movie_title: {
                'ranks': {
                    'timeout_actors': index+1
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        # add the movie to its list
        timeout_actors_list.append(capwords(movie_title))


def parse_binsider():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(binsider_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select('h2.slide-title-text')

    for item in list_items:
        # each item is formatted as such:
        # 1. "Citizen Kane" (1941)
        # strip the quotes and all whitespace
        item_text = item.text.strip()
        movie_index = item_text.split('.')[0]
        movie_title = item_text.strip(f'{movie_index}. ').replace('"', '')
        # construct data
        movie_data = {
            movie_title: {
                'ranks': {
                    'business_insider': int(movie_index)
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        binsider_list.append(movie_title)


def parse_ranker():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(ranker_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    # this one's fun. there's a lot going on in each of the list items,
    # so we're going to have parse every element out separately.

    # first, select all the containers
    list_items = soup.select('.listItem.listItem__h2')

    for item in list_items:
        movie_index = item.select_one('.listItem__rank').text.strip()
        movie_title = item.select_one('.listItem__title').text.strip()
        # now try to find the year of the movie (embedded ONLY in the description)
        movie_desc = item.select_one('.listItem__properties').text.strip()
        # use some fancy regex to select the year
        movie_year = re.findall(r'(\([12]\d{3}\))', movie_desc)[0]
        # sometimes, they decide to throw the year of production into the title
        # (because why not), so we need to account for that when adding the year ourselves.
        movie_title = movie_title.strip(movie_year)
        movie_title = ' '.join([movie_title, movie_year])
        # finally, save all the movie's data and append it to the list for the site
        movie_data = {
            movie_title: {
                'ranks': {
                    'ranker': movie_index
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        ranker_list.append(movie_title)


def parse_goodmovies():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(goodmovies_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select('p.list_movie_name')
    for index, item in enumerate(list_items):
        # the movie index is stored in plaintext inside item,
        # so we're going to just grab it from enumerate() instead
        movie_title = item.select_one('.list_movie_localized_name').text
        movie_year = item.find(
            'span', attrs={'itemprop': 'datePublished'}).text
        display_title = f'{movie_title} ({movie_year})'
        # construct the data 'nary
        # finally, save all the movie's data and append it to the list for the site
        movie_data = {
            display_title: {
                'ranks': {
                    'goodmovies': index+1
                }
            }
        }
        # update the movie data
        update_movie_data(movie_data)
        # append it to the list
        goodmovies_list.append(display_title)


def save_lists():
    with open('data/lists/imdb.txt', 'w') as f:

        for item in imdb_list:
            f.write(item + '\n')

    with open('data/lists/hollywood_reporter.txt', 'w') as f:
        for item in hwood_reporter_list:
            f.write(item + '\n')

    with open('data/lists/empire.txt', 'w') as f:
        for item in empire_list:
            f.write(item + '\n')

    with open('data/lists/tomatoes.txt', 'w') as f:
        for item in rt_list:
            f.write(item + '\n')

    with open('data/lists/wiki_top_grossing.txt', 'w') as f:
        for item in wiki_gross_list:
            f.write(item + '\n')


def main():
    parse_imdb()
    parse_hwood_reporter()
    parse_empire()
    parse_tomatoes()
    parse_wiki_gross()
    save_lists()
    # add all lists to a bigger list
    site_lists = [
        imdb_list,
        hwood_reporter_list,
        empire_list,
        rt_list,
        wiki_gross_list
    ]
    # loop thru all lists and add them to master_list
    for site_list in site_lists:

        for movie in site_list:
            if movie not in master_list.keys():
                master_list[movie] = 1
            else:
                master_list[movie] += 1

    for movie in master_list:
        print(movie, master_list[movie])


if __name__ == "__main__":
    parse_imdb()
