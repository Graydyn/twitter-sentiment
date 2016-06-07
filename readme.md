Notes about obtaining data:
Training data is much too large for github and may not be appropriate for every task.

For word2vec, train one through gensim or grab a pre-trained model from https://github.com/idio/wiki2vec

For the sentiment training data, Kaggle has an airlines tweets dataset that is labeled for sentiment that you can use (you will need to sign up).  No guarantees that the airline tweets
will appropriately train for your data though.

twitter_data.py will do a daily grab from the twitter API for a specific search term.  The twitter API won't allow you to grab tweets from >2 weeks ago
so you will need to run this daily for a long time in order to plot a trend.  For this reason the script is written as a webapp which will run on App Engine.

