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
from bokeh_constants import *

from scipy import stats, special


def draw_histogram(data_list, sigma,  bins="auto", density_histogram=False):
	# create histogram data
	frequency_list, bin_edges_list = make_histogram(data_list, bins=bins, density_histogram=density_histogram)
	left_edges = bin_edges_list[:-1]
	right_edges = bin_edges_list[1:]
	

	# do a cut off on both sides to show 68*
	count_left =0
	frequency_sum=0
	for cut_left, item  in enumerate(frequency_list):
		frequency_sum = frequency_sum+ item
		if frequency_sum > 0.16:
			print(cut_left, frequency_sum)
			break
	
	frequency_sum = 0
	for cut_right, item  in enumerate(frequency_list):
		frequency_sum = frequency_sum+ item
		if frequency_sum > 0.84:
			print(cut_right, frequency_sum)
			break
	
	cut_frequency_list =  [0]*(cut_left-1) + frequency_list[cut_left - 1:cut_right+1] +[0]*(len(frequency_list)-cut_right-1)
	
	
	data = {'frequency': frequency_list, 'left_edges': left_edges,
			'right_edges': right_edges,'cut_frequency':cut_frequency_list}
	
	source = ColumnDataSource(data=data)
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	my_title = Title(text="Modelled cash positions for S&P 500", align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")
	
	plot.yaxis.axis_label = 'Relative frequency'
	plot.axis.axis_label_text_font_size = "22px"
	plot.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	plot.y_range = Range1d(0.0, 0.06)
	
	plot.xaxis.axis_label = 'Cash positon'
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font
	plot.axis.major_label_text_font_size = "16px"  # double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	plot.x_range = Range1d(-0.6, 0.6)
	plot.xaxis[0].formatter = NumeralTickFormatter(format="0%")
	
	plot.xaxis.ticker= [-0.5,left_edges[cut_left-1],0,right_edges[cut_right], 0.5]
	plot.xaxis.major_label_overrides = {left_edges[cut_left-1]: '-12.5%', right_edges[cut_right]: '12.5%'}
	#plot.xaxis[0].ticker.desired_num_ticks = 4
	
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='gainsboro', line_color='black')  # legend='Underperforming monkey portfolios')
	
	
	
	r1 = plot.quad(
		bottom=0, top='cut_frequency', left='left_edges', right='right_edges', source=source,
		fill_color='gray', line_color='black')  # legend='Underperforming monkey portfolios')
	
	
	
	x = numpy.linspace(right_edges[0], right_edges[-1], 10000)
	pdf_normal = stats.norm.pdf(x, loc=0, scale=sigma) * (right_edges[2] - right_edges[1])
	plot.line(x, pdf_normal, line_color='black', line_width=4, alpha=0.7, legend_label="Normal distribution")
	
	plot.legend.label_text_font_size = "13pt"
	
	
	
	show(plot)
	return plot


def psi(xsi):
	
	return numpy.exp(-0.5*xsi**2)/(2*numpy.pi)**0.5


def Psi(xsi):
	
	return (1 + special.erf(xsi/2**0.5))/0.5

if __name__ == '__main__':
	
	result_list=[]
	sigma_list=[]
	compound_mu =0.132
	compound_sigma = 0.052
	
	
	for _ in range(10000):
		#sigma = numpy.random.default_rng().normal(compound_mu,compound_sigma)
		sigma= stats.norm.rvs(loc=compound_mu, scale = compound_sigma)
		
		a = (0 - compound_mu) / compound_sigma
		b = numpy.inf
		
		
		sigma_list.append(stats.truncnorm.rvs(a,b, loc=compound_mu, scale = compound_sigma))
		
			
		result_list.append(numpy.random.default_rng().normal(0.0,sigma_list[-1]))
		#result_list.append(numpy.random.default_rng().normal(0.0,1))
	
		
	print('Simulated mean of the compound distribution should be theoretically zero', numpy.mean(result_list))
	
	E = compound_mu + (compound_sigma*psi(a))/(1-Psi(a))
	print('Thoeretical expected value of truncated normal', E, 'versus theoretical approximation',
		  compound_mu, 'versus simulated', numpy.mean(sigma_list))
	
	Var = compound_sigma**2 *(1+a*psi(a)/(1-Psi(a)) - (psi(a)/(1-Psi(a)))**2  )
	
	print('Theoretical var value of truncated normal', Var, 'versus theoretical approximation',
		  compound_sigma**2, 'versus simulated', numpy.std(sigma_list)**2)
	
	print('******** Final Result of compound distribution ')
	print('Simulated mean of the compound distribution should be theoretically zero', numpy.mean(result_list))
	
	
	print('Theoretical var of compound distribution', E**2+Var, 'versus theoretical approximation ',
		  compound_mu ** 2 + (compound_sigma ** 2), 'versus simulated', numpy.std(result_list) ** 2)
	
	
	print('Simulated kurtosis', stats.kurtosis(result_list, fisher=False))

	result_list.sort()
	
	
	print('Standard deviation points', result_list[int((1-0.68)/2*len(result_list))],
		  result_list[int((1-(1-0.68)/2)*len(result_list))])
	
	

	print(stats.kstest(result_list, 'norm'))
	
	print(stats.shapiro(result_list))
	
	
	draw_histogram(result_list, compound_mu)