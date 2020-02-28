"""
Lots of websites disagree on what the top 100 movies of all time are, so I wanted to find out
what they actually are.

This scrapes a few different websites (I plan on adding more) and gets their top 100 list,
compiles all lists into one big list, and counts how often a movie appears in the list.

AUTHOR: Preston Carlton
DATE CREATED: Feb 28, 2020
"""
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from imdb import IMDb
import string
# all urls
imdb_url = "https://www.imdb.com/list/ls055592025/?mode=simple"
hwood_reporter_url = "https://www.hollywoodreporter.com/lists/100-best-films-ever-hollywood-favorites-818512"
empire_url = "https://www.empireonline.com/movies/features/best-movies-2/"
rt_url = "https://www.rottentomatoes.com/top/bestofrt/"
wiki_gross_url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
afi_url = "https://www.afi.com/afis-100-years-100-movies/"
timeout_url = "https://www.timeout.com/newyork/movies/best-movies-of-all-time"
timeout_actors_url = "https://www.timeout.com/newyork/movies/100-best-movies-as-chosen-by-actors"

msn_url = "https://www.msn.com/en-us/movies/gallery/100-best-movies-of-all-time/ar-AAAkjKL"
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

# nary to contain all the information about the movies
master_list = {}


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
        # access the div that contains the movie's IMDB rating(not implemented yet)
        rank_div = content.find('div', attrs={'class', 'col-imdb-rating'})
        # get all parts in the header_div
        header_elems = header_div.find_all('span')
        # access the movies rank in the list (not implemented yet)
        # movie_index = header_div.find('span',attrs={'class','lister-item-index'})
        movie_index = header_elems[0]
        # finally, get the movie's title (just kidding, this is ANOTHER WRAPPER)
        title_div = header_elems[1]
        # there's two elements in this; the movie's title and the year it was released. we want both.
        movie_title = title_div.find('a').text.strip()
        # get movie year
        movie_year = title_div.find('span').text.strip()
        # add year to the movie title
        display_title = ' '.join([movie_title, movie_year])

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
        # the only h1 in this div is the title
        movie_title = header_div.find('h1').text.strip()
        # the only h2 is the year
        movie_year = header_div.find('h2').text.strip()
        # combine year + title to get the full name
        display_title = ' '.join([movie_title, movie_year])
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
        movie_index = row_parts[0].text
        movie_rating = row_parts[1].text
        # this is already formatted how we want to display it
        display_title = row_parts[2].text.strip()
        num_reviews = row_parts[3].text
        # movie_title contains the year in the title, so we need to split that up
        movie_year = display_title.split(' ')[-1].strip()
        movie_title = display_title.strip(movie_year)
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
        wiki_gross_list.append(display_title)


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
        movie_name = '.'.join(item.text.split('.')[1:]).strip()
        afi_list.append(string.capwords(movie_name))


def parse_timeout():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(timeout_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select(
        '#content > article > div > div > div > div > div > article > div.card-content > header > h3 > a')

    for item in list_items[:-1]:
        print(item.text.strip())


def parse_timeout_actors():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(timeout_actors_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select(
        '#content > article > div > div > div > div > div > article > div.card-content > header > h3 > a')

    for item in list_items[:-1]:
        print(item.text.strip())


def parse_binsider():
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(timeout_actors_url, headers=hdr)
    page = urlopen(req)
    # convert the page into a bowl of soup
    soup = BeautifulSoup(page, 'html.parser')
    list_items = soup.select('#l-content > div > div.slide-title.clearfix > h2')
    # /html/body/section/section/section/section[3]/section/div/article/section[1]/div/section/div/div/div[2]/div/div[1]/h2

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
    parse_timeout_actors()
    
