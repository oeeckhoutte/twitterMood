from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import operator
import numpy as np
import matplotlib.pyplot as plt





def main():
    conf = SparkConf().setMaster("local[2]").setAppName("Streamer")
    sc = SparkContext(conf=conf)
    ssc = StreamingContext(sc, 10)   # Create a streaming context with batch interval of 10 sec
    ssc.checkpoint("checkpoint")

    pwords = load_wordlist("positive.txt")
    nwords = load_wordlist("negative.txt")
   
    counts = stream(ssc, pwords, nwords, 100)
    make_plot(counts)


def make_plot(counts):
    """
    Plot the counts for the positive and negative words for each timestep.
    Use plt.show() so that the plot will popup.
    """ 
    # YOUR CODE HERE
    pVal = []
    nVal = []
    for elem in counts:
        for sentiment,value in elem:
            if sentiment=="positive":
                pVal.append(int(value))
            elif sentiment=="negative":
                nVal.append(int(value))
    maxpVal = max(pVal)
    maxnVal = max(nVal)
    maxVal = max(maxpVal, maxnVal)

    plt.plot(range(len(pVal)), pVal, '.b-', linewidth = 1.25, label="positive")
    plt.plot(range(len(nVal)), nVal, '.g-',  linewidth = 1.25, label="negative")
    plt.legend(loc="upper left")
    plt.xlabel("Time step")
    plt.ylabel("Word Count")
    plt.axis([-1, len(pVal), 0, maxVal+40])
    plt.show()
    
    
    

def load_wordlist(filename):
    """ 
    This function should return a list or set of words from the given filename.
    """
    # YOUR CODE HERE
    wordList = []
    f = open(filename,"r")
    for word in f:
    	wordList.append(str(word).strip("\n"))
    return wordList

def checkWord(x,pwords,nwords):
    if x in pwords:
        return ("positive",1)
    elif x in nwords:
        return ("negative",1)
    return ("none",0)
	
		
def updateFunction(newValues, runningCount):
    if runningCount is None:
       runningCount = 0
    return sum(newValues, runningCount)  # add the new values with the previous running count to get the new count
		
    

def stream(ssc, pwords, nwords, duration):
    kstream = KafkaUtils.createDirectStream(
        ssc, topics = ['twitterstream'], kafkaParams = {"metadata.broker.list": 'localhost:9092'})
    tweets = kstream.map(lambda x: x[1].encode("ascii","ignore"))

    # Split each line into words
    tweets = tweets.flatMap(lambda line: line.split(" "))
    
    # Each element of tweets will be the text of a tweet.
    # You need to find the count of all the positive and negative words in these tweets.
    # Keep track of a running total counts and print this at every time step (use the pprint function).
    # YOUR CODE HERE
    tweets = tweets.map(lambda x:checkWord(x,pwords,nwords)).reduceByKey(lambda a, b: a + b)
    
    #print pwords
    # Let the counts variable hold the word counts for all time steps
    # You will need to use the foreachRDD function.
    # For our implementation, counts looked like:
    #   [[("positive", 100), ("negative", 50)], [("positive", 80), ("negative", 60)], ...]
    counts = []
    tweets.foreachRDD(lambda t,rdd: counts.append(rdd.collect()))
    totalCount = tweets.updateStateByKey(updateFunction)
    totalCount.pprint()
    ssc.start()                         # Start the computation
    ssc.awaitTerminationOrTimeout(duration)
    ssc.stop(stopGraceFully=True)

    return counts


if __name__=="__main__":
    main()
