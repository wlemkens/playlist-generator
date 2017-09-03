#!/usr/bin/python3

import sys
import os
import time
from scipy import *
from pylab import *
from scipy.io import wavfile
from pydub import AudioSegment
from tempfile import NamedTemporaryFile


N = 2048
H = int(N/4)

def speedChange(sound,speed=1.0):
	if speed==1.0:
		return sound
	if sound.channels>1:
		startTime = time.time()
		monoSound = sound.set_channels(1)
		endTime = time.time()
		print ("Converting to mono took {:f} seconds".format(endTime-startTime))
		return speedChangeChannel(monoSound,speed)
	else:
		return speedChangeChannel(sound,speed)
			
def speedChangeChannel(sound,tscale):
	startTime = time.time()
	tmpSrcFile = NamedTemporaryFile("w+b", suffix=".wav",delete=False)
	sound.export(tmpSrcFile.name,format="wav")
	tmpSrcFile.close()
	
	# read input and get the timescale factor
	(sr,signalin) = wavfile.read(tmpSrcFile.name)
	os.remove(tmpSrcFile.name)
	L = len(signalin)
	#for item in signalin:
		#print (item)
	# signal blocks for processing and output
	phi  = zeros(N)
	out = zeros(N, dtype=complex)
	sigout = zeros(int(L/tscale+N))

	# max input amp, window
	#amp = max(signalin)
	amp = max(signalin)
	win = hanning(N)
	p = 0
	pp = 0
	while p < L-(N+H):
		# take the spectra of two consecutive windows
		p1 = int(p)
		spec1 =  fft(win*signalin[p1:p1+N])
		spec2 =  fft(win*signalin[p1+H:p1+N+H])
		# take their phase difference and integrate
		phi += (angle(spec2) - angle(spec1))
		# bring the phase back to between pi and -pi
		for i in phi:
			while i > pi: i -= 2*pi
			while i <= -pi: i += 2*pi
		out.real, out.imag = cos(phi), sin(phi)
		# inverse FFT and overlap-add
		res = win*ifft(abs(spec2)*out)
		sigout[pp:pp+N] += res.real
		pp += H
		p += H*tscale

	#  write file to output, scaling it to original amp
	with NamedTemporaryFile("w+b", suffix=".wav",delete=False) as tmpModFile:
		wavfile.write(tmpModFile.name,sr,array(amp*sigout/max(sigout), dtype='int16'))
		newSound = AudioSegment.from_file(tmpModFile.name, "wav")
	endTime = time.time()
	print ("Resampling took {:f} seconds".format(endTime-startTime))
	return newSound

	
