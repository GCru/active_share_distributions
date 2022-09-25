from fundskill_utilities.setup_python_file_with_django import *  # this sets up the django environment

import numpy
from datetime import datetime, date
from statistics import median, stdev, mean
from scipy.stats import shapiro, chi, truncnorm, norm, lognorm
import csv

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d

from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, LinearAxis, Title, PrintfTickFormatter, NumeralTickFormatter

from bokeh.models.tickers import FixedTicker
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead, LabelSet
from bokeh.models import Range1d, SingleIntervalTicker
from bokeh.models import ColumnDataSource
from bokeh.layouts import row, gridplot, column, Spacer
from bokeh.io import export_png

from math import pi

from latex_label_utility import LatexLabel
import datetime

from fundskill_utilities.fundskill_utilities import change_to_next_month_end, change_to_another_month_end, \
	change_to_month_end, change_to_quarter_end, index

from fundskill_utilities.fundskill_shared_bokeh_utilities import HistogramPlot, setup_date_ticker_jump

from bokeh_constants import *

from make_histogram_procedure import make_histogram
from scaled_chi_max_likelihood import ChiMaxLikelihood, ChiKSTest
from trunc_normal_max_likelihood import TruncNormalMaxLikelihood

from shared_functions import load_data_from_csv_file, setup_date_range_and_benchmark_list


def draw_fitted_active_share_histogram(data_list, k, sigma_chi, mu, sigma_truncnormal, sigma_lognormal, scale_lognormal, title_text, bins="auto", density_histogram=False):
	# create histogram data
	
	frequency_list, bin_edges_list = make_histogram(data_list, bins=bins, density_histogram=density_histogram)
	left_edges = bin_edges_list[:-1]
	right_edges = bin_edges_list[1:]
	
	data = {'frequency': frequency_list, 'left_edges': left_edges,
				'right_edges': right_edges}
	source = ColumnDataSource(data=data)
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	my_title = Title(text=title_text, align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")

	
	if title_text == "S&P 500":
		max_x=0.4
		max_y=0.05
	else:
		max_x=0.30001
		max_y=0.07
		
	plot.xaxis.axis_label = 'Euclidean active share'
	#plot.xaxis.ticker = FixedTicker(ticks=[3, 5, 10, 15, 20, 25, 30, 35])

	plot.x_range = Range1d(0, max_x)
	plot.xaxis.ticker = SingleIntervalTicker(interval=0.05)
	
	plot.axis.major_label_text_font_size = "12pt"

	plot.xaxis[0].formatter = NumeralTickFormatter(format="0%")
	plot.min_border_right = 20
	#plot.min_border_bottom = 30

	plot.yaxis.axis_label = 'Relative frequency'
	plot.axis.axis_label_text_font_size = "22px"
	plot.yaxis[0].formatter = NumeralTickFormatter(format="0.1%")
	plot.y_range = Range1d(0.0, max_y)

	#plot.axis.axis_label_text_font_size = double_graph_axis_label_font_size
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font

	plot.axis.major_label_text_font_size = "18px" #double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='lightgrey', line_color='black')
	
	
	# draw curve fits
	x = numpy.linspace(0, right_edges[-1]+0.1, 10000)
	
	# draw fitted trunc norm
	a = (0 - mu) / sigma_truncnormal
	b = numpy.inf
	
	pdf_truncnormal = truncnorm.pdf(x, a, b, loc=mu, scale=sigma_truncnormal) * (right_edges[2] - right_edges[1])
	plot.line(x, pdf_truncnormal, line_color='black', line_width=4, alpha=0.7,
			  legend_label="Left-truncated normal")
	# draw fitted scaled chi
	df = k # (df*40)**(0.5)
	
	sigma_chi=sigma_chi
	if density_histogram == True:
		pdf_chi = chi.pdf(x, df, loc=0, scale=sigma_chi)
	
	else:
		pdf_chi = chi.pdf(x, df, loc=0, scale=sigma_chi) * (right_edges[2] - right_edges[1])
	
	plot.line(x, pdf_chi, line_color='black', line_width=4, alpha=0.7, legend_label="Scaled chi", line_dash='dashed')
	
	
	# draw fitted lognormal
	pdf_lognormal= lognorm.pdf(x,sigma_lognormal, scale=scale_lognormal)* (right_edges[2] - right_edges[1])
	plot.line(x, pdf_lognormal, line_color='slategray', line_width=4, alpha=0.7, line_dash='dotted',
			  legend_label="Scaled log-normal")
	
	plot.legend.label_text_font_size="13pt"
	
	return plot


def load_euclidean_active_share_data(benchmark_name):
	
	results_file_name = benchmark_name + '_active_share.csv'
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
	active_share_euclid_list, active_share_euclid_ex_cash_list, _, _ = load_data_from_csv_file(results_file_name)
	
	data_array = numpy.array(active_share_euclid_ex_cash_list) / 100
	
	return data_array


def draw_qq_plot(data_list, mu, sigma_truncnormal,  title_text, bins="auto", density_histogram=False, truncnormal=True, large_title=False):
	data_list.sort()
	
	# find z_values
	
	step = 1 / (len(data_list) + 1)
	
	if truncnormal:
		# draw fitted trunc norm
		a = (0 - mu) / sigma_truncnormal
		b = numpy.inf
	
		#pdf_truncnormal = truncnorm.pdf(x, a, b, loc=mu, scale=sigma_truncnormal) * (right_edges[2] - right_edges[1])
	
		std_normal_quintiles = [truncnorm.ppf(step * (i + 1), a,b,loc=mu, scale=sigma_truncnormal) for i in range(0, len(data_list))]
		
	else:
		std_normal_quintiles = [lognorm.ppf(step * (i + 1), mu, loc=0, scale=sigma_truncnormal) for i in
								range(0, len(data_list))]
	output_file("active_returns_scatter.html")
	p = figure(plot_width=500, plot_height=500)
	p.toolbar.logo = None
	p.toolbar_location = None
	
	min_x_axis_range = min(std_normal_quintiles)
	max_x_axis_range = max(std_normal_quintiles)
	
	my_title = Title(text=title_text,
					 text_font=font, text_font_size=double_graph_title_font_size,
					 align='center', text_line_height=1, vertical_align='middle')
	
	if large_title:
		my_title.text_font_size="28px"
	
	p.add_layout(my_title, 'above')
	p.min_border_right = 20
	p.min_border_bottom = 30
	
	p.x_range = Range1d(min_x_axis_range, max_x_axis_range)
	p.xgrid.visible = True
	p.xaxis[0].formatter = NumeralTickFormatter(format="0%")
	p.xaxis.axis_label = 'Theoretical active share quintiles'
	
	if truncnormal in (True, False):
		if title_text=='S&P 500':
			y_max = 0.6
			x_max = 0.35
			
		else:
			y_max=0.35
			x_max=0.3
	
	p.x_range = Range1d(0, x_max+0.000001)
	p.y_range = Range1d(0, y_max+0.00001)  #
	#p.ygrid.visible = False
	p.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	p.yaxis.axis_label = 'Funds\' active share quintiles'
	
	p.axis.axis_label_text_font_size = "22px" #double_graph_axis_label_font_size
	p.xaxis.axis_label_text_font = font
	p.yaxis.axis_label_text_font = font
	
	p.axis.major_label_text_font_size = "18px" #double_graph_major_label_font_size
	p.xaxis.major_label_text_font = font
	p.yaxis.major_label_text_font = font
	
	# add a circle renderer with a size, color, and alpha
	p.circle(std_normal_quintiles, data_list, size=2.0, color="black", alpha=1.0)
	
	# latex_y_axis_label = LatexLabel(
	#	text="\\text{Active risk, } \\mathbf{\sigma_{P-B}}",
	#	x=-16.6,
	#	y=2,
	#	# x_units="screen",
	#	# y_units="screen",
	#	render_mode="css",
	#	text_font_size=double_graph_latex_label_font_size,
	#	angle=90, angle_units="deg",
	#	background_fill_alpha=1)
	
	# p.add_layout(latex_y_axis_label)
	x = numpy.linspace(0,1,1000)
	y=x
	p.line(x,y, color="gray")
	
	
	return p


def create_single_qq_plot(benchmark_name, truncnormal=True, large_title=False):
	
	benchmark_text_name = benchmark_name[0:benchmark_name.find('TR') - 1]
	
	data_array = load_euclidean_active_share_data(benchmark_name)
	
	if truncnormal:
		# Fit truncnorm using Max linkelihood
		truncnormal_max_likelihood = TruncNormalMaxLikelihood(data_array)
		mu, sigma_truncnorm = truncnormal_max_likelihood.solve_mu_and_sigma()
		print('Trunc Normal maximum likelihood parameters (mu, sigma)', mu, sigma_truncnorm)
	else:
		# Fit lognormal
		sigma_lognorm, loc_lognormal, scale_lognormal = lognorm.fit(data_array, floc=0)
		print(sigma_lognorm, scale_lognormal)
		mu=sigma_lognorm
		sigma_truncnorm =scale_lognormal
	
	plot = draw_qq_plot(data_array,mu, sigma_truncnorm,
		title_text=benchmark_text_name, bins="auto", density_histogram=False,truncnormal=truncnormal, large_title=large_title)
	
	return plot


def create_panel_of_qq_fits( benchmark_name_left, benchmark_name_right, truncnormal=True,):
	
	benchmark_name = 'S&P 500 TR USD'  # 'Russell 2000 TR USD'  #
	plot_left = create_single_qq_plot(benchmark_name_left, truncnormal=truncnormal)
	
	plot_right = create_single_qq_plot(benchmark_name_right, truncnormal=truncnormal)
	
	
	panel_plot = row(plot_left, plot_right)
	
	show(panel_plot)
	return panel_plot


def create_grid_of_qq_fits(truncnormal=True, ):
	
	
	benchmark_list = ['Russell 2000 Value TR USD',
					  'Russell Mid Cap TR USD', 'Russell 2000 Growth TR USD',
					  'Russell Mid Cap Value TR USD', 'Russell Mid Cap Growth TR USD',
					  'Russell 3000 TR USD', 'Russell 1000 TR USD',
					  'Russell 1000 Value TR USD', 'Russell 1000 Growth TR USD',
					  ]
	
	plot_list =[]
	
	for benchmark_name in benchmark_list:
			plot_list.append(create_single_qq_plot(benchmark_name, truncnormal=truncnormal, large_title=True))
	
	#heading_mhtn = Div(text='<b>Manhattan Active Share</b>', style={'font-size': '15pt', 'color': 'black'}, height=30,
	#				   align='start', margin=(0, 0, 5, 60))
	
	first_row = row(plot_list[0:3])
	
	second_row = row(plot_list[3:6])
	
	third_row =row(plot_list[6:9])
	
	grid_plot = column(first_row, Spacer(height=20), second_row, Spacer(height=20), third_row)
	
	#grid_plot = column(first_row, second_row, third_row, gridplot(plot_list, ncols=3, width =350,toolbar_options={'logo': None})
	
	show(grid_plot)
	return grid_plot

	


def create_single_plot(benchmark_name):
	
	benchmark_text_name = benchmark_name[0:benchmark_name.find('TR')-1]
	
	data_array = load_euclidean_active_share_data(benchmark_name)
	
	# Fit scaled chi using Max likelihood
	chi_max_likelihood = ChiMaxLikelihood(data_array)
	k, sigma_chi = chi_max_likelihood.solve_k_sigma(k_guess=4)
	print('Scaled chi maximum likelihood parameters (k, sigma):', k, sigma_chi)
	
	# Fit truncnorm using Max linkelihood
	truncnormal_max_likelihood = TruncNormalMaxLikelihood(data_array)
	mu, sigma_truncnorm = truncnormal_max_likelihood.solve_mu_and_sigma()
	print('Trunc Normal maximum likelihood parameters (mu, sigma)', mu, sigma_truncnorm)
	
	# Fit lognormal
	sigma_lognorm, loc_lognormal,scale_lognormal = lognorm.fit(data_array, floc=0)
	print(sigma_lognorm, scale_lognormal)
	
	plot = draw_fitted_active_share_histogram(data_array, k, sigma_chi, mu, sigma_truncnorm, sigma_lognorm, scale_lognormal,
		title_text= benchmark_text_name, bins="auto", density_histogram=False)
	
	# pplot = sm.ProbPlot(test_array, fit=True)
	# pplot = sm.ProbPlot(numpy.array(histogram_active_share_list), fit=True)
	# fig = pplot.qqplot()
	# h = plt.title("Ex. 1")
	# plt.show()
	
	return plot


def create_panel_of_histogram_fits(date_range, benchmark_name_left, benchmark_name_right):
	
	plot_left = create_single_plot(benchmark_name_left)
	
	plot_right = create_single_plot(benchmark_name_right)
	
	panel_plot = row(plot_left, Spacer(width=15),plot_right)
	
	show(panel_plot)
	return panel_plot



def create_tables_of_fits(date_range, benchmark_list):
	
	dict_data=[]
	
	for benchmark_name in reversed(benchmark_list):
		data_array = load_euclidean_active_share_data(benchmark_name)
		
		# Fit scaled chi using Max likelihood
		chi_max_likelihood = ChiMaxLikelihood(data_array)
		k, sigma_chi = chi_max_likelihood.solve_k_sigma(k_guess=4)
		
		print(k,sigma_chi)
		chi_params = k, sigma_chi
		
		# Fit truncnorm using Max linkelihood
		truncnormal_max_likelihood = TruncNormalMaxLikelihood(data_array)
		mu, sigma_truncnorm = truncnormal_max_likelihood.solve_mu_and_sigma()
		truncnorm_params = mu, sigma_truncnorm
		
		print(benchmark_name, 'fitted parameters: (k, sigma_chi), (mu, sigma_truncnorm)', chi_params, truncnorm_params)
		
		print('Modelled cash positon stdev', (mu**2 +sigma_truncnorm**2)**0.5)
		
		dict_data.append({'benchmark': benchmark_name,
					'k':k, 'sigma_chi':sigma_chi, 'mu': mu, 'sigma_truncnorm':sigma_truncnorm, 'data_points':len(data_array)})
	
	
	csv_columns = ['benchmark','k','sigma_chi', 'mu', 'sigma_truncnorm', 'data_points']
	csv_file = "fitted_distribution_table.csv"
	with open(csv_file, 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
		writer.writeheader()
		for data in dict_data:
			writer.writerow(data)
	
	

if __name__ == '__main__':
	
	# set up date_range and benchmark
	
	date_range, benchmark_list =setup_date_range_and_benchmark_list()
	end_date = date(2007, 12, 31)
	date_range = [end_date]
	
	
	
	benchmark_name_left = 'S&P 500 TR USD'
	benchmark_name_right = 'Russell 2000 TR USD'
	
	
	#p1=create_panel_of_histogram_fits(date_range, benchmark_name_left, benchmark_name_right)
	
	#export_png(p1, filename="fit_chi_and_normal_histogram_plot.png")
	
	
	
	#p2 = create_panel_of_qq_fits(benchmark_name_left, benchmark_name_right, truncnormal=True)
	
	#export_png(p2, filename="fit_chi_and_normal_qq_plot.png")
	
	

	#create_single_qq_plot('Russell 3000 TR USD')  #'S&P 500 TR USD')  #

	
	create_tables_of_fits(date_range, benchmark_list)
	
	#p3=create_grid_of_qq_fits()
	
	#export_png(p3, filename="fit_chi_and_normal_qq_grid_plot.png")
