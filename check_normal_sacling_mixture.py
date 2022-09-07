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


def draw_histogram(data_list, sigma,  bins="auto", density_histogram=False):
	# create histogram data
	frequency_list, bin_edges_list = make_histogram(data_list, bins=bins, density_histogram=density_histogram)
	left_edges = bin_edges_list[:-1]
	right_edges = bin_edges_list[1:]
	
	data = {'frequency': frequency_list, 'left_edges': left_edges,
			'right_edges': right_edges}
	source = ColumnDataSource(data=data)
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	# plot.toolbar.logo = None
	# plot.toolbar_location = None
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='lightgrey', line_color='black')  # legend='Underperforming monkey portfolios')
	x = numpy.linspace(right_edges[0], right_edges[-1], 10000)
	pdf_normal = stats.norm.pdf(x, loc=0, scale=sigma) * (right_edges[2] - right_edges[1])
	plot.line(x, pdf_normal, line_color='green', line_width=4, alpha=0.7, legend_label="Normal distribution")
	
	#a = (0 - mu) / sigma
	#b = numpy.inf
	
	#pdf_truncnormal = truncnorm.pdf(x, a, b, loc=mu, scale=sigma) * (right_edges[2] - right_edges[1])
	#plot.line(x, pdf_truncnormal, line_color='blue', line_width=4, alpha=0.7,
	#		  legend_label="Truncated Normal distribution")
	
	show(plot)
	return plot


if __name__ == '__main__':
	
	result_list=[]
	compound_mu =0.12
	compound_sigma = 0.0
	for _ in range(10000):
		sigma = numpy.random.default_rng().normal(compound_mu,compound_sigma)
		if sigma<0:
			sigma=0
			
		result_list.append(numpy.random.default_rng().normal(0.0,sigma))
		#result_list.append(numpy.random.default_rng().normal(0.0,1))
			
	print(numpy.mean(result_list))
	print(numpy.std(result_list))
	print(stats.kurtosis(result_list, fisher=False))


	print(stats.kstest(result_list, 'norm'))
	
	print(stats.shapiro(result_list))
	
	
	draw_histogram(result_list, compound_mu)