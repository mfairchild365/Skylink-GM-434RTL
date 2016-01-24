import numpy as np
import time
from rtlsdr import RtlSdr

sdr = RtlSdr()

#config
sdr.samle_rate = 2.048e6
sdr.center_freq = 433888000
#sdr.freq_correction = 60
sdr.gain = 'auto'

#print(sdr.read_samples(512))

burst = 0
burst_time = 0
overall_avg = 20

while True:
	samples = sdr.read_samples(512*2);
	#run an FFT and take absolute value to get freq magnitudes
	freqs = np.absolute(np.fft.fft(samples))
	#ignore the mean/DC values at ends
	freqs = freqs[1:-1]
	#Shift FFT result positions to put center frequency in center
	freqs = np.fft.fftshift(freqs)
	#convert to decibels
	freqs = 20.0*np.log10(freqs)

	mean = np.mean(freqs)
	min = np.min(freqs)
	max = np.max(freqs)
	diff = max - mean
	percent_diff = overall_avg/max

	if 0 > mean:
		#This sometimes happens at the start of the application
		continue

	if 0.4 > percent_diff:
		burst+=1
		burst_time = time.time()
		print "mean: " + str(mean) + " max: " + str(max) + " Diff: " + str(diff)
		print percent_diff 
	elif 5 < burst and time.time() > burst_time+5:
		print "BURST: " + str(burst)
		burst = 0
		burst_time = 0	
	elif 1 <= burst and time.time() > burst_time+5:
		print "TIMEOUT"
		burst = 0
		burst_time = 0
	else:
		overall_avg = np.mean([overall_avg, mean])
		#print overall_avg



#	for freq in freqs:
#		if (freq > 50):
#			print freq
		


