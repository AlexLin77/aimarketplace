import numpy as np 
import pandas as pd
import pickle
import json
from tensorflow import keras
import tensorflow_datasets as tfds
from sklearn.model_selection import train_test_split

ratings = pd.read_csv('../../static/ratings.csv')
users = tfds.load('movielens/100k-ratings', split='train')

ratings = ratings.drop(['timestamp'], axis=1)

users_df = tfds.as_dataframe(users)

users_to_ages = {}
for elt in users_df[['user_id', 'bucketized_user_age']].dropna().drop_duplicates().iterrows():
    user_id = elt[1]['user_id'].decode('utf-8')
    users_to_ages[int(user_id)] = elt[1]['bucketized_user_age']

users_to_genders = {}
for elt in users_df[['user_id', 'user_gender']].dropna().drop_duplicates().iterrows():
    user_id = elt[1]['user_id'].decode('utf-8')
    users_to_genders[int(user_id)] = elt[1]['user_gender']

users_to_occupations = {}
for elt in users_df[['user_id', 'user_occupation_text']].dropna().drop_duplicates().iterrows():
    user_id = elt[1]['user_id'].decode('utf-8')
    user_occupation = elt[1]['user_occupation_text'].decode('utf-8')
    users_to_occupations[int(user_id)] = user_occupation

ratings['age'] = ratings['userId'].map(users_to_ages)
ratings['gender'] = ratings['userId'].map(users_to_genders)
ratings['occupation'] = ratings['userId'].map(users_to_occupations)

unique_users = ratings.userId.unique()
users_map = {i:val for i,val in enumerate(unique_users)}
inv_users_map = {val:i for i,val in enumerate(unique_users)}

unique_items = ratings.movieId.unique()
items_map = {i:val for i,val in enumerate(unique_items)}
inv_items_map = {val:i for i,val in enumerate(unique_items)}

unique_ages = ratings.age.unique()
ages_map = {i:val for i,val in enumerate(unique_ages)}
inv_ages_map = {val:i for i,val in enumerate(unique_ages)}

unique_genders = ratings.gender.unique()
genders_map = {i:val for i,val in enumerate(unique_genders)}
inv_genders_map = {val:i for i,val in enumerate(unique_genders)}

unique_occupations = ratings.occupation.unique()
occupations_map = {i:val for i,val in enumerate(unique_genders)}
inv_occupations_map = {val:i for i,val in enumerate(unique_occupations)}

ratings['userId'] = ratings['userId'].map(inv_users_map)
ratings['movieId'] = ratings['movieId'].map(inv_items_map)
ratings['age'] = ratings['age'].map(inv_ages_map)
ratings['gender'] = ratings['gender'].map(inv_genders_map)
ratings['occupation'] = ratings['occupation'].map(inv_occupations_map)

trainset, testset = train_test_split(ratings, test_size=0.25)

# items layer
items_in = keras.layers.Input(shape=[1])
items_embed = keras.layers.Embedding(input_dim=unique_items.shape[0]+1, output_dim=20, input_length=1)(items_in)
items_out = keras.layers.Reshape([20])(items_embed)

# users layer
users_in = keras.layers.Input(shape=[1])
users_embed = keras.layers.Embedding(input_dim=unique_users.shape[0]+1, output_dim=20, input_length=1)(users_in)
users_out = keras.layers.Reshape([20])(users_embed)

# ages layer
ages_in = keras.layers.Input(shape=[1])
ages_embed = keras.layers.Embedding(input_dim=unique_ages.shape[0]+1, output_dim=20, input_length=1)(ages_in)
ages_out = keras.layers.Reshape([20])(ages_embed)

# genders layer
genders_in = keras.layers.Input(shape=[1])
genders_embed = keras.layers.Embedding(input_dim=unique_genders.shape[0]+1, output_dim=20, input_length=1)(genders_in)
genders_out = keras.layers.Reshape([20])(genders_embed)

# regions layer
occupations_in = keras.layers.Input(shape=[1])
occupations_embed = keras.layers.Embedding(input_dim=unique_occupations.shape[0]+1, output_dim=20, input_length=1)(occupations_in)
occupations_out = keras.layers.Reshape([20])(occupations_embed)

all_users_out = keras.layers.Concatenate()([users_out, ages_out, genders_out, occupations_out])

all_layers = keras.layers.Concatenate()([all_users_out, items_out])
all_layers = keras.layers.Dense(64, activation='relu')(all_layers)
final = keras.layers.Dense(1, activation='relu')(all_layers)
model = keras.Model([users_in, ages_in, genders_in, occupations_in, items_in], final)

opt = keras.optimizers.Adam()
model.compile(optimizer=opt, loss='mean_squared_error')

# FINISH THIS
model.fit([trainset['userId'], trainset['age'], trainset['gender'], trainset['occupation'], 
           trainset['movieId']], trainset['rating'], batch_size=16, epochs=11, verbose=1, 
          validation_data=([testset['userId'], testset['age'], testset['gender'], testset['occupation'], testset['movieId']], testset['rating']))

dicts_compiled = {}
dicts_compiled['users_map'] = users_map
dicts_compiled['inv_users_map'] = inv_users_map
dicts_compiled['items_map'] = items_map
dicts_compiled['inv_items_map'] = inv_items_map
dicts_compiled['ages_map'] = ages_map
dicts_compiled['inv_ages_map'] = inv_ages_map
dicts_compiled['genders_map'] = genders_map
dicts_compiled['inv_genders_map'] = inv_genders_map
dicts_compiled['occupations_map'] = occupations_map
dicts_compiled['inv_occupations_map'] = inv_occupations_map

pickle.dump(dicts_compiled, open('dicts-compiled.npz', 'wb'))

model.save('nnmodel.h5')



