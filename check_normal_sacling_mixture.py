import numpy
from datetime import date
from statistics import stdev, mean
from math import pi, log, sqrt
from scipy.stats import kstest, kurtosis, skew, skewtest, jarque_bera, wasserstein_distance, median_abs_deviation
from scipy.special import erf
from scipy import optimize

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d, PrintfTickFormatter, NumeralTickFormatter, Title
from bokeh.layouts import row
from bokeh.models import ColumnDataSource

from make_histogram_procedure import make_histogram

from scipy import stats

if __name__ == '__main__':
	
	result_list=[]
	for i in range(1):
		for j in range (5000):
			
			sigma = numpy.random.default_rng().normal(50,0.1)
			if sigma<0:
				sigma=0
			
			result_list.append(numpy.random.default_rng().normal(0.0,sigma))
			#result_list.append(numpy.random.default_rng().normal(0.0,1))
			
	print(numpy.mean(result_list))
	print(numpy.std(result_list))


	print(stats.kstest(result_list, 'norm'))
	
	print(stats.shapiro(result_list))
	
	
	hist, bin_edges = make_histogram(results_list)