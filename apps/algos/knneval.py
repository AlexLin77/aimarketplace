import pandas as pd
import json
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors

df = pd.read_csv('../../static/ratings.csv')

df = df.drop(['timestamp'], axis=1)

df_mtx = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)

final_mtx = csr_matrix(df_mtx)

trainset, testset= train_test_split(final_mtx, test_size=0.15)

model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
model.fit(trainset)

with open('index-to-movie.json', 'r') as jfile:
    index_to_movie = json.load(jfile)

with open('movie-to-index.json', 'r') as jfile:
    movie_to_index = json.load(jfile)

df['genres'] = df['genres'].map(lambda x: x.replace('|', ', '))

total_p = 0
total_r = 0
denom = 0

for movie in list(movie_to_index.keys())[:30]:

    input_row = df.loc[df.title == movie, 'genres']
    input_genres = ''.join(input_row.tolist())
    input_genres = input_genres.split(',')
    # print(len(input_genres))

    temp = []

    for row in df.iterrows():
        if row[1]['title'] != movie:
            comp_str = row[1]['genres']
            comp_genres = comp_str.split(',')

            num = 0
            denom = 0

            all_genres = []
            if len(input_genres) >= len(comp_genres):
                for genre in comp_genres:
                    if genre in input_genres:
                        num += 1
                        denom += 1
                        all_genres.append(genre)
                    else:
                        denom += 1
                        all_genres.append(genre)
                for genre in input_genres:
                    if genre not in all_genres:
                        denom += 1
                        all_genres.append(genre)
            else:
                for genre in input_genres:
                    if genre in comp_genres:
                        num += 1
                        denom += 1
                        all_genres.append(genre)
                    else:
                        denom += 1
                        all_genres.append(genre)
                for genre in comp_genres:
                    if genre not in all_genres:
                        denom += 1
                        all_genres.append(genre)
            
            score = num / denom

            temp.append((row[1]['title'], score))

    relevant_items = []

    for tup in temp:
        if tup[1] >= 0.5:
            relevant_items.append(tup[0])

    selected = df_mtx.loc[[movie_to_index[movie]]]
    final_selected = csr_matrix(selected)

    dist, ind = model.kneighbors(selected, n_neighbors=10)

    retrieved = ind.size
    relevant = 0
    for i in range(ind.size):
        idx = str(ind[0, i].item(0))
        if idx in index_to_movie:
            movie_title = index_to_movie[idx]
            if movie_title in relevant_items:
                relevant += 1
      
    precision = relevant / retrieved
    # print('local')
    # print(precision)
    denom += 1
    total_p += precision
    # print('total')
    # print(total)
    recall = relevant / len(relevant_items)
    total_r += recall

avg_precision = total_p / denom
avg_recall = total_r / denom

print('final')
print(avg_precision)
print(avg_recall)

