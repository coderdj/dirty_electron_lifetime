# Get a random 50 waveforms and plot
import pymongo
import matplotlib.pyplot as plt
import numpy as np
#from pax.plugins.peak_processing import BasicProperties
from tqdm import tqdm
import os

mongo_string = "mongodb://daq:%s@localhost:27017/admin"%os.environ['MONGO_PASSWORD']
db = "data"
coll = "xebra_drift_test_2"
pretrigger_window=50
posttrigger_window =50
max_std = 50 # maximum allowed standard deviation for baseline

client = pymongo.MongoClient(mongo_string)
collection = client[db][coll]
cursor = collection.find().sort("time", 1)

def GetRoughWidth(data):

    imax = np.argmax(data)
    maxiter = max([imax, len(data)-imax])
    sumdata = data.sum()
    rquant=0.
    rise_time=0
    width=0
    for i in range(0, maxiter):
        if width!=0 and rise_time !=0:
            break
        if imax-i>=0:
            if data[imax-i]<.1*data[imax] and rise_time==0:
                rise_time=i
            rquant+=data[imax-i]
        if i!=0 and imax+i<len(data):
            rquant+=data[imax+i]
        if rquant>0.5*sumdata and width==0:
            width=i
    if width==0:
        width=None
    if rise_time==0:
        rise_time=None
    #print("WIDTH AND RISE TIME")
    #print(width)
    #print(rise_time)
    #plt.figure()
    #plt.plot(range(len(data)), data)
    #plt.show()
                                                                
    return width, rise_time


def ExtractPeakProperties(data):

    avgbl = []
    
    # Get baseline before trigger
    pre_trigger_baseline = data[:pretrigger_window]    
    ptmean = pre_trigger_baseline.mean()
    ptstd = pre_trigger_baseline.std()
    if ptstd < max_std:
        avgbl.append(ptmean)

    # Get baseline for after trigger
    post_trigger_baseline = data[-posttrigger_window:]
    pstmean = post_trigger_baseline.mean()
    pststd = post_trigger_baseline.std()
    if pststd < max_std:
        avgbl.append(pstmean)

    # Take average of 'good' BL's
    try:
        baseline = sum(avgbl)/float(len(avgbl))
    except:
        # No good baseline found, sorry
        return None

    # Get integral
    integral = -1.*(float(data.sum()) - baseline*float(len(data)))

    corrected_data = np.array([-1.*(d-baseline) for d in data])
    
    # Get maximum
    index_of_maximum = np.argmax(corrected_data)
    maximum = data[index_of_maximum]

    # Get range_xp_area
    width, rise_time = GetRoughWidth(corrected_data)

    
    ret = {
        'ptmean': ptmean,
        'pstmean': pstmean,
        'ptstd': ptstd,
        'pststd': pststd,
        'baseline': baseline,
        'integral': integral,
        'window_length': len(data),
        'maximum': maximum,
        'index_of_maximum': index_of_maximum,
        #'range_25p_area': retrange[0],
        'range_50p_area': width,
        #'range_75p_area': retrange[2]
        'rise_time': rise_time
    }
    
    return ret

docs = []
for doc in tqdm(cursor):
    payload = doc['data']
    data = np.fromstring(payload, dtype=np.int16)
    pp = ExtractPeakProperties(data)
    if pp is None:
        continue
    pp['channel'] = doc['channel']
    pp['time'] = doc['time']

    if pp['rise_time']<=5 and pp['range_50p_area']<=5:
        pp['type']=1
    else:
        pp['type']=2
    
    docs.append(pp)

import pickle
pickle.dump(docs, open("extracted_peaks.pkl", "wb"))

                                                                                                    
