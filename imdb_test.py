from imdb import IMDb

# create an instance of the IMDb class
ia = IMDb()

# search for the godfather
godfather = ia.search_movie("The godfather (1972)",results=1)
godfather = ia.search
print(godfather[0].movieID)
