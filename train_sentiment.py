import numpy as np
import pandas as pd
import gensim
import string
from nltk.corpus import stopwords
from gensim.corpora import WikiCorpus
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

def scrubTweet(tweet):
    newTweets = list()
    oldTweets = tweet.split()
    for word in oldTweets:
        if (not '@' in word) and (not '#' in word):
            newTweets.append(word.translate(None, string.punctuation).lower())

    return newTweets

def create_bag_of_centroids( wordlist, word_centroid_map ):

    num_centroids = max( word_centroid_map.values() ) + 1
    bag_of_centroids = np.zeros( num_centroids, dtype="float32" )

    for word in wordlist:
        if word in word_centroid_map:
            index = word_centroid_map[word]
            bag_of_centroids[index] += 1

    return bag_of_centroids

train_df = pd.read_csv('data/training.csv', header=None)
test_df = pd.read_csv('data/test.csv', header=None)

train = train_df[5] #the actual tweet is in the 5th column
test = test_df[5]

train = train.apply(scrubTweet).tolist()
#remove empty lists
train = [x for x in train if x]

model = gensim.models.Word2Vec.load("data/en_1000_no_stem/en.model")
print model.similarity('woman', 'man')
print model.similarity('woman', 'banana')

#adding to the existing model fails, probably because the old model was trained under an older version of gensim
#i bet getting this working would improve performance
#model.train(word2vecTrain, total_examples=len(word2vecTrain))

word_vectors = model.syn0
num_clusters = word_vectors.shape[0] / 5
kmeans_clustering = KMeans( n_clusters = num_clusters )
idx = kmeans_clustering.fit_predict( word_vectors )

word_centroid_map = dict(zip( model.index2word, idx ))
train_centroids = np.zeros( (train.size, num_clusters), \
    dtype="float32" )

counter = 0
for tweet in train:
    train_centroids[counter] = create_bag_of_centroids( tweet, \
        word_centroid_map )
    counter += 1

test_centroids = np.zeros(( test.size, num_clusters), \
    dtype="float32" )

counter = 0
for tweet in test:
    test_centroids[counter] = create_bag_of_centroids( test, \
        word_centroid_map )
    counter += 1

#Haven't done much cross-validation here, other models may work just as well or better
forest = RandomForestClassifier(n_estimators = 100)

forest = forest.fit(train_centroids,train_df[2])
result = forest.predict(test_centroids)

#write results
output = pd.DataFrame(data={"id":test["id"], "sentiment":result})
output.to_csv( "BagOfCentroids.csv", index=False, quoting=3 )

