from django.conf import settings

from apps.store.models import Product

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd
import json

class Userdata(object):
    def __init__(self):
        with open('static/ratings.json', 'r') as jfile:
            dataset = json.load(jfile)

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
                if self.dataset[username][product_title] + weight > 5:
                    self.dataset[username][product_title] = 5
                else:
                    self.dataset[username][product_title] += weight
        
        with open('static/ratings.json', 'w') as jfile:
            json.dump(self.dataset, jfile, indent=4)

