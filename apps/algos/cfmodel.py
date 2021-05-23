import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import mean_squared_error
from scipy.sparse import csr_matrix

df = pd.read_csv('../../static/ratings.csv')

df = df.drop(['timestamp'], axis=1)

df_mtx = df.pivot(index='movieId', columns='userId', values='rating').fillna(0)

final_mtx = csr_matrix(df_mtx)

trainset, testset= train_test_split(final_mtx, test_size=0.15)

model = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=10)
model.fit(trainset)

# for vector in testset:
#     distances, indices = model.kneighbors(vector, n_neighbors=3)
#     print(indices)

filename = 'knnmodel.sav'
pickle.dump(model, open(filename, 'wb'))
