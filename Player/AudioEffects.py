#!/usr/bin/python3

import sys
from scipy import *
from pylab import *
from scipy.io import wavfile
from pydub import AudioSegment

N = 2048
H = int(N/4)

def speedChange(wavFilename,outputFilename,tscale):
	# read input and get the timescale factor
	(sr,signalin) = wavfile.read(wavFilename)
	L = len(signalin)
	#for item in signalin:
		#print (item)
	# signal blocks for processing and output
	phi  = zeros(N)
	out = zeros(N, dtype=complex)
	sigout = zeros(int(L/tscale+N))

	# max input amp, window
	#amp = max(signalin)
	amp = signalin.max()
	win = hanning(N)
	p = 0
	pp = 0
	signalin1 = [sign1 for sign1,sign2 in signalin]
	#signalin2 = [sign2 for sign1,sign2 in signalin]
	signalin = signalin1
	while p < L-(N+H):
		# take the spectra of two consecutive windows
		p1 = int(p)
		spec1 =  fft(win*signalin[p1:p1+N])
		spec2 =  fft(win*signalin[p1+H:p1+N+H])
		# take their phase difference and integrate
		phi += (angle(spec2) - angle(spec1))
		#for item in phi:
			#print(item)
		# bring the phase back to between pi and -pi
		for i in phi:
			while i > pi: i -= 2*pi
			while i <= -pi: i += 2*pi
		out.real, out.imag = cos(phi), sin(phi)
		# inverse FFT and overlap-add
		res = win*ifft(abs(spec2)*out)
		#for item in res:
			#print(item)
		sigout[pp:pp+N] += res.real
		pp += H
		p += H*tscale
	out1 = sigout
	sigout = zeros(int(L/tscale+N))
	#signalin = signalin2
	#while p < L-(N+H):
		## take the spectra of two consecutive windows
		#p1 = int(p)
		#spec1 =  fft(win*signalin[p1:p1+N])
		#spec2 =  fft(win*signalin[p1+H:p1+N+H])
		## take their phase difference and integrate
		#phi += (angle(spec2) - angle(spec1))
		##for item in phi:
			##print(item)
		## bring the phase back to between pi and -pi
		#for i in phi:
			#while i > pi: i -= 2*pi
			#while i <= -pi: i += 2*pi
		#out.real, out.imag = cos(phi), sin(phi)
		## inverse FFT and overlap-add
		#res = win*ifft(abs(spec2)*out)
		##for item in res:
			##print(item)
		#sigout[pp:pp+N] += res.real
		#pp += H
		#p += H*tscale
	#out2 = sigout
	#sigout = np.array(zip(out1,out2))
	#  write file to output, scaling it to original amp
	wavfile.write(outputFilename,sr,array(amp*sigout/max(sigout), dtype='int16'))
	return AudioSegment.from_file(outputFilename, "wav")

