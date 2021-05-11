from .data import Dataset

from apps.store.models import Product

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd


def refresh(request):
    ds = Dataset(request)
    
    if request.user.is_authenticated:
        curr_user = request.user.username
    else:
        curr_user = 'guest'
    
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

    vectorizer = TfidfVectorizer(stop_words='english')

    tfidf_matrix = vectorizer.fit_transform(df['description']).toarray()

    cossim_matrix = np.zeros((len(tfidf_matrix), len(tfidf_matrix)))

    for i in range(len(item_to_index)):
        for j in range(len(item_to_index)):
            if i != j:
                num = np.multiply(tfidf_matrix[i], tfidf_matrix[j])
                new_num = np.sum(num)

                norm1 = np.linalg.norm(tfidf_matrix[i])
                norm2 = np.linalg.norm(tfidf_matrix[j])

                cossim_matrix[i, j] = new_num / (norm1 * norm2)
            else:
                cossim_matrix[i, j] = 0

    top_results = int(len(items)/3)
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

