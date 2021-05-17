from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import pandas as pd

df = pd.read_csv('sample-data.csv')

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

np.save('cossim-matrix.npy', cossim_matrix)