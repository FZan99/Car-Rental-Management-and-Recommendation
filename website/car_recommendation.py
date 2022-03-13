import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3

cnx = sqlite3.connect(r'website/carrental.db')
car_rental = pd.read_sql_query("SELECT * FROM Car", cnx)

cols = [ 'brand','submodel', 'type', 'transmission']
car_rental['details'] = car_rental[cols].apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

counts = dict()

for i in car_rental.index:
  for g in car_rental.loc[i,'details'].split(' '):
    if g not in counts:
      counts[g] = 1
    else:
      counts[g] = counts[g] + 1


from sklearn.feature_extraction.text import TfidfVectorizer

tfidf_vector = TfidfVectorizer(stop_words='english') # create an object for TfidfVectorizer
tfidf_matrix = tfidf_vector.fit_transform(car_rental['details']) # apply the object to the genres column

from sklearn.metrics.pairwise import linear_kernel

sim_matrix = linear_kernel(tfidf_matrix,tfidf_matrix) # create the cosine similarity matrix

def get_SUBMODEL_from_index(index):

  return car_rental[car_rental.index == index]['submodel'].values[0]


def get_ID_from_index(index):

  return car_rental[car_rental.index == index]['id'].values[0]

def get_TYPE_from_index(index):

  return car_rental[car_rental.index == index]['type'].values[0]

def get_TRANSMISSION_from_index(index):

  return car_rental[car_rental.index == index]['transmission'].values[0]

def get_IMGNAME_from_index(index):

  return car_rental[car_rental.index == index]['img_name'].values[0]


def get_index_from_SUBMODEL(submodel):

  return car_rental[car_rental.submodel == submodel ].index.values[0]


from fuzzywuzzy import fuzz


# create a function to find the closest title
def matching_score(a,b):

  return fuzz.ratio(a,b)

# a function to convert index to title
def get_SUBMODEL_from_index(index):

  return car_rental[car_rental.index == index]['submodel'].values[0]


# the function to return the most similar title to the words a user types
def find_closest_SUBMODEL(SUBMODEL):

  leven_scores = list(enumerate(car_rental['submodel'].apply(matching_score, b=SUBMODEL)))
  sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True)
  closest_SUBMODEL = get_SUBMODEL_from_index(sorted_leven_scores[0][0])
  distance_score = sorted_leven_scores[0][1]

  return closest_SUBMODEL, distance_score


def contents_based_recommender(car_user_likes, how_many):

  closest_SUBMODEL, distance_score = find_closest_SUBMODEL(car_user_likes)

  if distance_score == 100:

    car_index = get_index_from_SUBMODEL(closest_SUBMODEL)
    car_list = list(enumerate(sim_matrix[int(car_index)]))
    similar_car = list(filter(lambda x:x[0] != int(car_index), sorted(car_list,key=lambda x:x[1], reverse=True))) # remove the typed movie itself

    # print('Here\'s the list of cars similar to '+'\033[1m'+str(closest_SUBMODEL)+'\033[0m'+'.\n')

    lists = []
    j=1
    for i,s in similar_car[:how_many]:
        
        lists.append(str(get_ID_from_index(i))) 
        j = j+1
    return lists
    

  else:
    print('Did you mean '+'\033[1m'+str(closest_SUBMODEL)+'\033[0m'+'?','\n')

    car_index = get_index_from_SUBMODEL(closest_SUBMODEL)
    car_list = list(enumerate(sim_matrix[int(car_index)]))
    similar_car = list(filter(lambda x:x[0] != int(car_index), sorted(car_list,key=lambda x:x[1], reverse=True)))

    # print('Here\'s the list of car similar to '+'\033[1m'+str(closest_SUBMODEL)+'\033[0m'+'.\n')

    
    lists = []
    j=1
    for i,s in similar_car[:how_many]:
        
        lists.append(str(get_ID_from_index(i))) 
        j = j+1
    return lists 

import random
option1, option2, option3 = random.sample(range(1, 20), 3)


def car1 (lists):

  
  return lists[random.randrange(0, 5)]

def car2 (lists):

  
  return lists[random.randrange(6, 10)]

def car3 (lists):

  
  return lists[random.randrange(11, 15)]


    
    
    
        
      
      

    