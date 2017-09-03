#!/usr/bin/python3

import sys
import os
import time
from scipy import *
from pylab import *
from scipy.io import wavfile
from pydub import AudioSegment
from pydub.utils import make_chunks
from pydub import effects

from tempfile import NamedTemporaryFile


N = 2048
H = int(N/4)

def testPerformance(sound):
	# Take the first second to resample
	sampleSize = 1000
	if (len(sound)<sampleSize):
		print ("Warning, sample is too short to test performance!")
		return 0
	elif (len(sound)>2*sampleSize):
		offset = len(sound)/2
	else:
		offset = 0
	sample = sound[offset:offset+sampleSize]
	startTime = time.time()
	speedChange(sample,0.5)
	endTime = time.time()
	# If it takes more time to process a sample as the duration of the sample, we will not be able to convert real time (return will be < 1)
	return sampleSize/((endTime-startTime)*1000)
	
def speedChange(sound,speed=1.0):
	if speed==1.0:
		return sound
	if sound.channels>1:
		monoSound = sound.set_channels(1)
		return speedChangeChannel(monoSound,speed)
	else:
		return speedChangeChannel(sound,speed)
			
def speedChangeChannel(sound,tscale):
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
	return newSound

def fallbackSpeedChange(sound,speed=1.0):
	if sound.channels>1:
		sound = sound.set_channels(1)
	if speed>1.0:
		return speedUp(sound,speed)
	elif speed <1.0:
		return slowDown(sound,speed)
	else:
		return sound

def recursiveMerge(chunks1,chunks2,crossfade):
	if len(chunks1)+len(chunks2)>1:
		if len(chunks1)>len(chunks2):
			chunks2+=[AudioSegment.empty()]
		newChunks = []
		i = 0
		for chunk1,chunk2 in zip(chunks1,chunks2):
			i+=1
			if (len(chunk2)>crossfade):
				newChunk = chunk1.append(chunk2,crossfade=crossfade)
			else:
				newChunk = chunk1+chunk2
			newChunks += [newChunk]
		return recursiveMerge(newChunks[::2],newChunks[1::2],crossfade)
	else:
		return chunks1[0]

def slowDown(sound,speed):
	chunkSize = 50
	crossfade = 0
	multiplier = 1.0/speed
	ms_to_add_per_chunk = chunkSize*(multiplier-1)+crossfade
	chunks = make_chunks(sound,chunkSize)
	last_chunk = chunks[-1]
	chunks = [chunk+chunk[:ms_to_add_per_chunk] for chunk in chunks[:-1]]+[last_chunk]
	out = recursiveMerge(chunks[::2],chunks[1::2],crossfade)
	return out

def speedUp(sound,speed):
	return effects.speedup(sound,speed)
