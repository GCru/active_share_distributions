from scipy.stats import chi, kstest, ks_2samp, norm, lognorm, truncnorm
from scipy.special import psi, gamma, erf
from scipy.optimize import fsolve, minimize

import numpy

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d, PrintfTickFormatter, NumeralTickFormatter, Title, DatetimeTickFormatter
from bokeh.layouts import row
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.models.tickers import FixedTicker
from bokeh.io import export_png

from bokeh_constants import *

from shared_with_active_risk_paper import make_histogram


def draw_trunc_normal_histogram(data_list, mu, sigma, bins="auto", density_histogram=False):
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
	x = numpy.linspace(0, right_edges[-1], 10000)
	pdf_normal = norm.pdf(x, loc=mu, scale=sigma) * (right_edges[2] - right_edges[1])
	plot.line(x, pdf_normal, line_color='green', line_width=4, alpha=0.7, legend_label="Normal distribution")
	
	
	a= (0-mu)/sigma
	b = numpy.inf
	
	pdf_truncnormal = truncnorm.pdf(x, a,b, loc=mu, scale=sigma) * (right_edges[2] - right_edges[1])
	plot.line(x, pdf_truncnormal, line_color='blue', line_width=4, alpha=0.7, legend_label="Truncated Normal distribution")
	


	show(plot)
	return plot


def generate_random_trunc_normal(mu, sigma, N):
	""" Scipy generate random normal truncated at a = 0
	:param k:
	:param sigma:
	:param N:
	:return:
	"""
	
	myclip_a =  0
	a = (myclip_a - mu)/sigma
	b = numpy.inf
	
	print(truncnorm.stats(a,b, loc=mu, scale=sigma, moments='mvsk'))
	
	data = truncnorm.rvs(a, b, size=N, scale = sigma, loc=mu )
	#data = norm.rvs(size=N, scale=sigma, loc=mu)

	return data


class TruncNormalMaxLikelihood(object):
	
	def __init__(self, data):
		self.data = data
		self.N = len(data)
	
	def log_likelihood_function(self, x0):
		
		mu=x0[0]
		sigma=x0[1]
		
		if sigma <= 0:
			sigma=0.0000001
		if mu<=0:
			mu=0.000001

		f = -self.N * numpy.log(sigma) - self.N* numpy.log(2*numpy.pi)/2
		
		f = f - self.N* numpy.log(1- 0.5*(1+erf(-mu/(sigma*(2**0.5)))))
		
		f = f - numpy.dot(self.data - mu, self.data - mu)/(2*sigma*sigma)
		
		return -f
	
	def solve_mu_and_sigma(self, mu_guess=0.1, sigma_guess=0.05):
		
		res = minimize(self.log_likelihood_function, [mu_guess, sigma_guess], bounds=((0,None), (0,None)), method='Powell')
		
		return res.x[0], res.x[1]



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	N = 10000
	mu= 1    # parameter for untruncatetd normal
	sigma = 0.8 # parameter for untruncated normal
	
	data = generate_random_trunc_normal(mu, sigma, N)
	
	
	truncnormal_max_likelihood = TruncNormalMaxLikelihood(data)
	print('truncnorm stats', numpy.mean(data), numpy.std(data))
	
	
	mu, sigma  = truncnormal_max_likelihood.solve_mu_and_sigma()
	
	print('solved', mu, sigma)
	
	print(truncnormal_max_likelihood.log_likelihood_function([mu,sigma]))
	
	print(truncnormal_max_likelihood.log_likelihood_function([1, 0.8]))# Genrate random data for test
	
	
	plot_density = draw_trunc_normal_histogram(data, mu, sigma, density_histogram=False)
	show(plot_density)