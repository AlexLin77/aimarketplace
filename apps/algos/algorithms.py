from .data import Userdata

from apps.store.models import Product

from sklearn.feature_extraction.text import TfidfVectorizer
from surprise import Dataset, Reader
from surprise import KNNBasic
from surprise.model_selection import train_test_split
from collections import defaultdict
import numpy as np
import pandas as pd


def refresh(request):
    ds = Userdata(request)
    
    if request.user.is_authenticated:
        curr_user = request.user.username
    else:
        curr_user = 'guest'
    
    if curr_user in ds.dataset:
        prefs = ds.dataset[curr_user]
        sorted_prefs = {key: val for key, val in sorted(prefs.items(), key=lambda item: item[1])}

        lst = list(sorted_prefs.keys())

        featured = description_sim(lst)
        print(featured)

        for product in Product.objects.all():
            if product.title in featured:
                print(product.title)
                product.is_featured = True
                product.save()


def description_sim(items):

    df = pd.read_csv('static/sample-data.csv')

    item_to_index = {}
    index_to_item = {}
    for i in range(len(df)):
        desc = df.loc[i, 'description']
        item_name = desc.split(' - ')[0]
        item_to_index[item_name] = i
        index_to_item[i] = item_name
    
    cossim_matrix = np.load('static/cossim-matrix.npy')

    top_results = int(len(items)/2)
    total_vector = np.zeros(len(cossim_matrix))
    item_indexes = []
    for i in range(top_results):
        # centroid vector
        item_idx = item_to_index[items[i]]
        item_indexes.append(item_idx)
        total_vector += cossim_matrix[item_idx]
    
    total_vector /= top_results
    
    results = []
    for idx, score in enumerate(total_vector):
        if idx not in item_indexes:
            results.append((index_to_item[idx], score))
    results = sorted(results, key=lambda x: x[1], reverse=True)

    result_items = [tup[0] for tup in results]

    return result_items[:5]

def collab_filter(request):
    ds = Userdata(request)

    data_dict = defaultdict(list)

    for user in ds:
      for item in ds[user]:
          score = ds[user][item]
          data_dict['users'].append(user)
          data_dict['items'].append(item)
          data_dict['score'].append(score)
    
    df = pd.DataFrame(data_dict)
    reader = Reader(rating_scale=(0, 30))

    data = Dataset.load_from_df(df, reader)

    # may change train/test proportions
    trainset, testset = train_test_split(data, test_size=0.25)

    # toggle between user-based and item-based
    sim_options = {
        'name': 'cosine',
        'user_based': False
    }
    algo = KNNBasic(sim_options)

    predict = algo.test(testset)

    if request.user.is_authenticated:
        user_check = request.user.username
    else:
        user_check = 'guest'

    results = []
    for user, item, real, est, _ in predict:
        if user == user_check:
            results.append((item, est))
    
    results = sorted(results, key=lambda x: x[1], reverse=True)

    results_items = [tup[0] for tup in results]

    return results_items[:5]



