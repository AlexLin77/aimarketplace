from django.conf import settings

from apps.store.models import Product

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

class Userdata(object):
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
                if self.dataset[username][product_title] + weight > 30:
                    self.dataset[username][product_title] = 30
                else:
                    self.dataset[username][product_title] += weight
        
        self.save()

    def save(self):
        self.session[settings.ALGOS_SESSION_ID] = self.dataset
        self.session.modified = True

        print(self.dataset)
    
    def clear(self):
        del self.session[settings.ALGOS_SESSION_ID]
        self.session.modified = True

