from django.conf import settings

from apps.store.models import Product

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

class Dataset(object):
    def __init__(self, request):
        self.session = request.session
        dataset = self.session.get(settings.ALGOS_SESSION_ID)

        if not dataset:
            dataset = self.session[settings.ALGOS_SESSION_ID] = {}

        self.dataset = dataset
    
    def add(self, product, username, weight):
        product_title = str(product.title)

        if username not in self.dataset:
            self.dataset[username] = {}
            self.dataset[username][product_title] = weight
        else:
            if product_title not in self.dataset[username]:
                self.dataset[username][product_title] = weight
            elif product_title in self.dataset[username]:
                self.dataset[username][product_title] += weight
        
        self.save()

    def save(self):
        self.session[settings.ALGOS_SESSION_ID] = self.dataset
        self.session.modified = True

        print(self.dataset)

        # df = pd.read_csv('static/sample-data.csv')

        # inverted_index = {}
        # for i in range(len(df)):
        #     desc = df.loc[i, 'description']
        #     item_name = desc.split(' - ')[0]
        #     inverted_index[item_name] = i

        # vectorizer = TfidfVectorizer(stop_words='english')

        # tf_matrix = vectorizer.fit_transform(df['description']).toarray()

        # print(len(df))
        # print(len(inverted_index))
        # print(len(tf_matrix))
    
    def clear(self):
        del self.session[settings.ALGOS_SESSION_ID]
        self.session.modified = True



