import pandas as pd
import json

df = pd.read_csv('movies.csv')

movie_to_index = {}
index_to_movie = {}

for row in df.iterrows():
    movie_to_index[row[1]['title']] = row[1]['movieId']
    index_to_movie[int(row[1]['movieId'])] = row[1]['title']

with open('movie-to-index.json', 'w') as jfile:
    json.dump(movie_to_index, jfile, indent=4)

with open('index-to-movie.json', 'w') as json_file:
    json.dump(index_to_movie, json_file, indent=4)



