from scipy.stats import chi, kstest, ks_2samp, norm
from scipy.special import psi, gamma
from scipy.optimize import fsolve, minimize

import numpy


def generate_random_normal(N, scale):
	""" Scipy generate random chi values
	:param k:
	:param sigma:
	:param N:
	:return:
	"""
	
	data = norm.rvs( size=N, loc=0, scale=scale)
	
	return data



if __name__ == '__main__':
	
	# Examine the theoretical relationship between Euclidean and Manhattan active share using Gearys paper
	# The larger the value of N the better the relation ship works
	# The larger the scale the less accurate
	N=10
	scale = 1
	ratio=[]
	
	for count in range(1000):
	
		data = generate_random_normal(N, scale) #scale=1/N**0.5)
	
		Euclidean_distance = (numpy.dot(data, data)**0.5)
	
		
	
		Manhattan_distance = numpy.sum(numpy.abs(data))/2
		
		ratio.append(2*Manhattan_distance/(Euclidean_distance*N**0.5))
		
		print('Manhattan distance:', Manhattan_distance)
		print('Euclidean distance', Euclidean_distance)
		
		print('Manhattan distance calculated from Euclidean distance:', 0.5*Euclidean_distance * 0.79788456 * N ** 0.5)
		print()
		
		
	# Check Geary's numbers
	print('Geary\'s mean of ratio when n is 10: ', (2.1/numpy.pi)**0.5)
	print('Actual mean:',numpy.mean(ratio) )
		
	print('Geary\'s variance of ratio when n is 10: ', 0.00375)
	print('Actual variance:', numpy.var(ratio))
	
	
	
	