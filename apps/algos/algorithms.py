from .data import Userdata
from .meta import Metadata

from apps.store.models import Product

from sklearn.model_selection import train_test_split
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import MaxAbsScaler
from tensorflow.keras.models import load_model
from tensorflow import argsort
from scipy.sparse.linalg import svds
from collections import defaultdict
import pickle
import numpy as np
import pandas as pd
import json
import tensorflow_datasets as tfds

def refresh(request):
    ds = Userdata()
    
    if request.user.is_authenticated:
        curr_user = request.user.username

        featured = []

        nn_results = nn_exec(curr_user)

        for result in nn_results:
            featured.append(result)

        with open('static/ratings.json', 'r') as jfile:
            dataset = json.load(jfile)

        if curr_user in dataset:
            prefs = dataset[curr_user]
            sorted_prefs = {key: val for key, val in sorted(prefs.items(), key=lambda item: item[1])}
            
            lst = list(sorted_prefs.keys())

            knn_results = cf_exec(lst[:5])

            for result in knn_results:
                featured.append(result)
        
        print(featured)

        for product in Product.objects.all():
            if product.title in featured:
                print(product.title)
                product.is_featured = True
                product.save()
            if product.title not in featured and product.is_featured:
                product.is_featured = False
                product.save()

    else:
          curr_user = 'guest'

          with open('static/ratings.json', 'r') as jfile:
            dataset = json.load(jfile)
    
          if curr_user in dataset:
              prefs = dataset[curr_user]
              sorted_prefs = {key: val for key, val in sorted(prefs.items(), key=lambda item: item[1])}

              lst = list(sorted_prefs.keys())

              content_filter(lst)

              # call jaccard function here
              featured = content_filter(lst)
              print(featured)

              for product in Product.objects.all():
                  if product.title in featured:
                      print(product.title)
                      product.is_featured = True
                      product.save()
                  if product.title not in featured and product.is_featured:
                      product.is_featured = False
                      product.save()

def content_filter(items):

    df = pd.read_csv('static/movies.csv')

    df['genres'] = df['genres'].map(lambda x: x.replace('|', ', '))

    results = []

    for movie in items:
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

        temp = sorted(temp, key=lambda x: x[1], reverse=True)

        for elt in temp[:2]:
            results.append(elt[0])
    
    final = []

    with open('static/ratings.json', 'r') as jfile:
        dataset = json.load(jfile)
    
    for result in results:
        if result in dataset['guest']:
            if dataset['guest'][result] < 1:
                final.append(result)
        else:
            final.append(result)
    
    return final


# def description_sim(items):

#     df = pd.read_csv('static/sample-data.csv')

#     item_to_index = {}
#     index_to_item = {}
#     for i in range(len(df)):
#         desc = df.loc[i, 'description']
#         item_name = desc.split(' - ')[0]
#         item_to_index[item_name] = i
#         index_to_item[i] = item_name
    
#     cossim_matrix = np.load('static/cossim-matrix.npy')

#     top_results = int(len(items)/2)
#     total_vector = np.zeros(len(cossim_matrix))
#     item_indexes = []
#     for i in range(top_results):
#         # centroid vector
#         item_idx = item_to_index[items[i]]
#         item_indexes.append(item_idx)
#         total_vector += cossim_matrix[item_idx]
    
#     total_vector /= top_results
    
#     results = []
#     for idx, score in enumerate(total_vector):
#         if idx not in item_indexes:
#             results.append((index_to_item[idx], score))
#     results = sorted(results, key=lambda x: x[1], reverse=True)

#     result_items = [tup[0] for tup in results]

#     return result_items[:5]

def user_svd(user):

    df = pd.read_csv('static/movies.csv')
    ratings = pd.read_csv('static/ratings.csv')

    ratings = ratings.drop(['timestamp'], axis=1)
    ratings_mtx = ratings.pivot(index='movieId', columns='userId', values='rating').fillna(0)

    with open('index-to-movie.json', 'r') as jfile:
        index_to_movie = json.load(jfile)

    idx_to_mv = {i:val for i, val in enumerate(ratings_mtx.index)}

    U, S, Vt = svds(ratings_mtx, k=30)

    Sd = np.diag(S)

    predictions = np.dot(np.dot(U, Sd), Vt)

    pdf = pd.DataFrame(predictions)

    # print(pdf.head())

    user_id = 0
    user_ratings = sorted(pdf[user_id], reverse=True)

    top_idxs = []
    for i in range(20):
        idx = pdf.index[pdf[user_id] == user_ratings[i]]
        top_idxs.append(idx[0])

    top_movies = []
    for idx in top_idxs:
        movie_idx = idx_to_mv[idx]
        if str(movie_idx) in index_to_movie:
            movie_title = index_to_movie[str(movie_idx)]
            top_movies.append(movie_title)

    for movie in top_movies:
        print(movie)


def cf_exec(items):

    filename = 'apps/algos/knnmodel.sav'

    model = pickle.load(open(filename, 'rb'))

    df = pd.read_csv('static/ratings.csv')

    df = df.drop(['timestamp'], axis=1)

    df_mtx = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)

    # final_mtx = csr_matrix(df_mtx)

    # trainset, testset= train_test_split(final_mtx, test_size=0.15)

    # # scaler = MaxAbsScaler()
    # # trainset_scaled = scaler.fit_transform(trainset)

    # model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
    # model.fit(trainset)

    # print(trainset.shape)

    results = []

    with open('static/ratings.json', 'r') as jfile:
        dataset = json.load(jfile)

    with open('static/movie-to-index.json', 'r') as jfile:
        movie_to_index = json.load(jfile)

    with open('static/index-to-movie.json', 'r') as jfile:
        index_to_movie = json.load(jfile)
    
    movie_idxs = []
    for movie in items:
        movie_idxs.append(movie_to_index[movie])
    
    selected = df_mtx.loc[movie_idxs]

    final_selected = csr_matrix(selected)
    dist, ind = model.kneighbors(final_selected, n_neighbors=10)

    # get closest ones only
    for i in range(int(dist.size/5)):
        score = dist[0, i].item(0)
        idx = str(ind[0, i].item(0))
        if idx in index_to_movie and idx not in items:
            results.append((index_to_movie[str(idx)], score))
    
    results = sorted(results, key=lambda x: x[1], reverse=False)

    result_items = [tup[0] for tup in results]

    return result_items[:10]

def nn_exec(user):
    
    model = load_model('apps/algos/nnmodel.h5')

    with open('static/ratings.json', 'r') as jfile:
        dataset = json.load(jfile)
    
    with open('static/users.json', 'r') as jfile:
        users = json.load(jfile)

    with open('static/movie-to-index.json', 'r') as jfile:
        movie_to_index = json.load(jfile)

    with open('static/index-to-movie.json', 'r') as jfile:
        index_to_movie = json.load(jfile)
    
    dicts_compiled = pickle.load(open('apps/algos/dicts-compiled.npz', 'rb'))
    
    user_only = []
    if user not in dataset or user not in users:
        return []
    
    # movie names to movie indices
    # only movies not seen?
    for movie in movie_to_index:
        if movie not in dataset[user]:
            mov_idx = movie_to_index[movie]
            user_only.append(mov_idx)

    df = pd.DataFrame(user_only, columns=['movieId'])

    user_age = users[user][0]
    user_gender = users[user][1]
    user_occupation = users[user][2]

    if user_age < 18:
        df['age'] = 1.0
    elif user_age >= 18 and user_age < 25:
        df['age'] = 18.0
    elif user_age >= 25 and user_age < 35:
        df['age'] = 25.0
    elif user_age >= 35 and user_age < 45:
        df['age'] = 35.0
    elif user_age >= 45 and user_age < 50:
        df['age'] = 45.0
    elif user_age >= 50 and user_age < 56:
        df['age'] = 50.0
    elif user_age >= 56:
        df['age'] = 56.0
    
    if user_gender == 'male':
        df['gender'] = True
    else:
        df['gender'] = False

    df['occupation'] = user_occupation

    df.insert(0, 'userId', 671)

    # print(df.head())

    inv_items_map = dicts_compiled['inv_items_map']
    items_map = dicts_compiled['items_map']
    inv_ages_map = dicts_compiled['inv_ages_map']
    inv_genders_map = dicts_compiled['inv_genders_map']
    inv_occupations_map = dicts_compiled['inv_occupations_map']

    # movie indices to model indices
    df['movieId'] = df['movieId'].map(inv_items_map)
    df['age'] = df['age'].map(inv_ages_map)
    df['gender'] = df['gender'].map(inv_genders_map)
    df['occupation'] = df['occupation'].map(inv_occupations_map)

    # print(df['movieId'].nunique())

    # print(df.head())

    df = df.dropna()
    df['movieId'] = df['movieId'].astype('int64')

    # print(df.head())

    model_index_to_position = {i:idx for i, idx in enumerate(df['movieId'])}

    predictions = model.predict([df['userId'], df['age'], df['gender'], df['occupation'], df['movieId']])

    # top 10 results
    sort = argsort(predictions.flatten(), direction='DESCENDING')[:10]
    top = sort.numpy()

    results = []

    for idx in top:
        model_idx = model_index_to_position[idx]
        movie_idx = items_map[model_idx]
        movie_name = index_to_movie[str(movie_idx)]
        results.append(movie_name)

    return results

    





