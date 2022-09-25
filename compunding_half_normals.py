"Test the actual and approximate moments of chi"

import numpy
from scipy.stats import halfnorm, norm
from bokeh.io import output_file, show

from make_histogram_procedure import draw_histogram

if __name__ == '__main__':
	
	# assume weights are drawn from halfnormal, constructed from normal with theta the standard deviation
	
	random_numbers=[]
	for count in range(10000):
	
		phi =(norm.rvs(loc=2,scale=1))
		if phi<0:
			phi=0
		phi=1
		random_numbers.append(halfnorm.rvs(size=1, scale=phi))
	
		#random_numbers.append(phi)
	
	print(numpy.mean(random_numbers), (2/numpy.pi)**0.5)
	
	plot=draw_histogram(random_numbers)
	
	show(plot)
	
	