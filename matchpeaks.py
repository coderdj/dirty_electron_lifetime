import numpy as np
import pickle
from tqdm import tqdm
import matplotlib.pyplot as plt
ep = pickle.load(open("extracted_peaks.pkl", "rb"))

interactions = []
for i, peak in tqdm(enumerate(ep)):
    if peak['type']==1 or i==0:
        continue
    if ep[i-1]['type']!=1:
        continue

    dt = peak['time']-ep[i-1]['time']
    #print(peak['time'])
    #print(ep[i-1]['time'])
    #print(peak['time']-ep[i-1]['time'])
    #break
    interactions.append({'s1': ep[i-1]['integral'],
                         's2': peak['integral'],
                         'drift_time': dt/100,
                         's2_width': peak['range_50p_area']})
    
ls2s = [np.log10(a['s2']) for a in interactions]
s2s = [(a['s2']) for a in interactions]
s1s = [(a['s1']) for a in interactions]
dts = [a['drift_time'] for a in interactions]
from matplotlib.colors import LogNorm
plt.figure()
#plt.scatter(dts, s2s)
plt.hist2d(dts, ls2s, bins=(np.arange(0, 50, .1), np.arange(2, 6, .05)), norm=LogNorm())
plt.xlabel("Drift time (microseconds)")
plt.ylabel("log10(S2 area) digitizer units")
plt.show()
widths=[a['s2_width'] for a in interactions]
plt.figure()
#plt.scatter(dts,widths)
plt.hist2d(dts, widths, bins=(np.arange(0, 50, .1), np.arange(0, 50, 1)), norm=LogNorm())
plt.xlabel("dt (mus)")
plt.ylabel("s2 width (samples)")
plt.show()

#widths = [a['range_50p_area'] for a in ep]
#s2s = [a['integral'] for a  in ep]
#rise_times=[a['rise_time'] for a in ep]
#plt.figure()
#plt.hist2d(rise_times, widths, bins=(np.arange(0, 250, 1), np.arange(0, 250,1)), norm=LogNorm())
#plt.show()
