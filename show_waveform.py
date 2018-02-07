# Get a random 50 waveforms and plot
import pymongo
import matplotlib.pyplot as plt
import numpy as np
import os

mongo_string = "mongodb://daq:%s@localhost:27017/admin"%os.environ["MONGO_PASSWORD"]
db = "data"
coll = "xebra_drift_test_2"
limit=50

client = pymongo.MongoClient(mongo_string)
collection = client[db][coll]
cursor = collection.find().limit(limit)

integrals = []
for doc in cursor:
    payload = doc['data']
    data = np.fromstring(payload, dtype=np.int16)
    baseline = 0
    dat = 0
    for i, databin in enumerate(data):
        if i < 10:
            baseline+=databin
        else:
            dat+=(baseline/10.)-databin
            integrals.append(dat)
    plt.figure()
    plt.plot(range(len(data)), data)
    plt.show()
print(integrals)
                                                                                                    
