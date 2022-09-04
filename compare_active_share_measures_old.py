from fundskill_utilities.setup_python_file_with_django import *  # this sets up the django environment

import numpy
from datetime import datetime, date
from statistics import median, stdev, mean
from scipy.stats import linregress
import csv

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d

from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, LinearAxis, Title, PrintfTickFormatter, NumeralTickFormatter

from bokeh.models.tickers import FixedTicker
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead, LabelSet
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource
from bokeh.layouts import row
from bokeh.io import export_png

from math import pi

from latex_label_utility import LatexLabel
import datetime

from fundskill_utilities.fundskill_utilities import change_to_next_month_end, change_to_another_month_end, \
	change_to_month_end, change_to_quarter_end, index

from fundskill_utilities.fundskill_shared_bokeh_utilities import HistogramPlot, setup_date_ticker_jump

from bokeh_constants import *

from make_histoogram_procedure import make_histogram
from chi_distribution_plot_old import ChiMaxLikelihood, draw_active_share_histogram, ChiKSTest


def load_data_from_csv_file(file_name):
	active_share_mhtn_list = []
	active_share_mhtn_ex_cash_list = []
	active_share_euclid_list = []
	active_share_euclid_ex_cash_list = []
	quarter_end_list = []
	
	with open(file_name, mode='r') as file:
		# reading the CSV file
		csv_file = csv.DictReader(file)
		
		# displaying the contents of the CSV file
		for line in csv_file:
			quarter_end_str = line['quarter_end']
			print(quarter_end_str)
			quarter_end_date = datetime.datetime.strptime(quarter_end_str, '%b%Y')
			quarter_end_date = change_to_month_end(quarter_end_date)
			quarter_end_list.append(quarter_end_date)
			
			active_share_mhtn_list.append(float(line['active_share_mhtn']))
			active_share_mhtn_ex_cash_list.append(float(line['active_share_mhtn_ex_cash']))
			active_share_euclid_list.append(float(line['active_share_euclid']))
			active_share_euclid_ex_cash_list.append(float(line['active_share_euclid_ex_cash']))
	
	return quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		   active_share_euclid_list, active_share_euclid_ex_cash_list


def draw_active_share_time_series(
		date_range, index_name, median_mhtn_list, mhtn_10_list, mhtn_90_list, median_euclid_list, euclid_10_list,
		euclid_90_list):
	output_file("active_share_time_series.html")
	
	p = figure(plot_width=int(500), plot_height=500)
	
	x_range = []
	for i, d in enumerate(date_range):
		x_range.append(i)
	
	x_axis_tickers = [change_to_month_end(date_range[i]).strftime('%b %y')
					  for i in range(len(date_range))]
	
	override_dict = setup_date_ticker_jump(x_axis_tickers)
	
	median_mhtn_list = [item / 2 for item in median_mhtn_list]
	mhtn_10_list = [item / 2 for item in mhtn_10_list]
	mhtn_90_list = [item / 2 for item in mhtn_90_list]
	
	source = ColumnDataSource(
		data={'x_range': x_range, 'median_mhtn_list': median_mhtn_list, 'median_euclid_list': median_euclid_list,
			  'mhtn_10_list': mhtn_10_list, 'mhtn_90_list': mhtn_90_list, 'euclid_10_list': euclid_10_list,
			  'euclid_90_list': euclid_90_list})
	
	p.circle(x='x_range', y='median_mhtn_list', color="black", source=source)
	
	p.varea(x='x_range', y1='euclid_10_list', y2='euclid_90_list', color='lightgrey', source=source)
	p.circle(x='x_range', y='median_euclid_list', color="black", source=source)
	
	if index_name == 'S&P 500 TR USD':
		the_title = "S&P 500"
	
	else:
		the_title = "Russell 2000"
	
	my_title = Title(text=the_title, text_font=font, text_font_size=double_graph_title_font_size,
					 align='center', text_line_height=1, vertical_align='middle')
	
	p.add_layout(my_title, 'above')
	
	p.toolbar.logo = None
	p.toolbar_location = None
	
	# set up Y-axis
	p.yaxis.axis_label = 'Active Share '
	# p.yaxis.axis_label_standoff = 30
	p.ygrid.visible = False
	p.y_range = Range1d(0, 50)
	p.yaxis[0].formatter = PrintfTickFormatter(format="%2.0f%%")
	
	# right hand side axis
	p.extra_y_ranges = {"NumStations": Range1d(start=0, end=100)}
	
	if index_name == 'S&P 500 TR USD':
		extra_axis_label = ''
	else:
		extra_axis_label = "Active Share"
	
	p.yaxis.axis_label_standoff = 20
	p.add_layout(LinearAxis(y_range_name="NumStations", axis_label=extra_axis_label), 'right')
	p.yaxis[1].formatter = PrintfTickFormatter(format="%2.0f%%")
	
	# set up x_axis
	p.xaxis.axis_label = 'Quarter ends'
	# p.xaxis.axis_label_standoff = 0
	p.xgrid.visible = False
	p.x_range = Range1d(-0.5, len(x_range) - 0.5)
	p.xaxis.ticker = x_range
	p.xaxis.major_label_overrides = override_dict
	p.xaxis.major_label_orientation = pi / 4
	
	# add latex labels
	
	x_range_half = len(x_range) // 2 - 7
	p.axis.axis_label_text_font_size = double_graph_axis_label_font_size
	p.xaxis.axis_label_text_font = font
	p.yaxis.axis_label_text_font = font
	
	p.axis.major_label_text_font_size = double_graph_major_label_font_size
	p.xaxis.major_label_text_font = font
	p.yaxis.major_label_text_font = font
	
	if index_name == 'S&P 500 TR USD':
		y_height_mhtn = 42.5
		y_height_euclid = 17
	else:
		y_height_mhtn = 45
		y_height_euclid = 15
	
	latex_euclid_label = LatexLabel(
		text="\\mathbf{\\longleftarrow A_{\\mathrm{Euclid}}} \\text{ \small{(lhs axis)}}",
		x=x_range_half - 7,
		y=y_height_euclid + 1,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font=font, text_font_size=double_graph_latex_label_font_size,
		background_fill_alpha=1)
	
	p.add_layout(latex_euclid_label)
	
	latex_mhtn_label = LatexLabel(
		text="\\mathbf{ A_{\\mathrm{Mhtn}}} \\text{ \small{(rhs axis)}} \\longrightarrow",
		x=x_range_half - 2,
		y=y_height_mhtn,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font='Helvetica', text_font_size=double_graph_latex_label_font_size,
		background_fill_alpha=1)
	
	p.add_layout(latex_mhtn_label)
	
	# show(p)
	
	return p


def draw_histogram(active_share_list, is_euclid=True):
	if is_euclid:
		output_file("euclid_active_share_histogram.html")
	else:
		output_file("mhnt_active_share_histogram.html")
	
	frequency_list, bin_edges_list = make_histogram(active_share_list)
	
	left_edges = bin_edges_list[:-1]
	right_edges = bin_edges_list[1:]
	data = {'frequency': frequency_list, 'left_edges': left_edges, 'right_edges': right_edges}
	source = ColumnDataSource(data=data)
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	if is_euclid:
		my_title = "Euclidean Active Share"
	else:
		my_title = "Manhattan Active Share"
	
	my_title = Title(text=my_title, align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")
	
	plot.x_range = Range1d(0.0, right_edges[-1])
	plot.xaxis.axis_label = ' '
	plot.xaxis[0].formatter = PrintfTickFormatter(format="%2.0f%%")
	plot.min_border_right = 20
	plot.min_border_bottom = 30
	
	plot.yaxis.axis_label = 'Relative Frequency'
	plot.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	plot.y_range = Range1d(0.0, 0.05)
	
	plot.axis.axis_label_text_font_size = double_graph_axis_label_font_size
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font
	
	plot.axis.major_label_text_font_size = double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	
	if is_euclid:
		label_text = "\\mathbf{ A_{\\mathrm{Euclid}}}"
		x_position = 21
	else:
		label_text = "\\mathbf{ A_{\\mathrm{Mhtn}}}"
		x_position = 50
	
	latex_x_axis_label = LatexLabel(
		text=label_text,
		x=x_position,
		y=-0.0035,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size=double_graph_latex_label_font_size,
		background_fill_alpha=1)
	
	plot.add_layout(latex_x_axis_label)
	
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='lightgrey', line_color='black')  # legend='Underperforming monkey portfolios')
	
	return plot


def load_data(index_name, date_range):
	results_file_name = index_name + '_active_share.csv'
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
	active_share_euclid_list, active_share_euclid_ex_cash_list = load_data_from_csv_file(results_file_name)
	
	median_euclid_list = []
	euclid_10_list = []
	euclid_90_list = []
	
	mean_euclid_list = []
	stdev_euclid_list = []
	
	median_mhtn_list = []
	mhtn_10_list = []
	mhtn_90_list = []
	idx = 0
	
	for quarter_end_date in date_range:
		
		euclid_list = []
		mhtn_list = []
		
		while quarter_end_date == quarter_end_list[idx]:
			
			euclid_list.append(active_share_euclid_list[idx])
			mhtn_list.append(active_share_mhtn_list[idx])
			
			idx = idx + 1
			
			if idx == len(quarter_end_list):
				break
		
		euclid_list.sort()
		
		euclid_10_list.append(euclid_list[len(euclid_list) // 10])
		euclid_90_list.append(euclid_list[(len(euclid_list) - 1) - len(euclid_list) // 10])
		median_euclid_list.append(median(euclid_list))
		
		mhtn_list.sort()
		
		mhtn_10_list.append(mhtn_list[len(mhtn_list) // 10])
		mhtn_90_list.append(mhtn_list[(len(mhtn_list) - 1) - len(mhtn_list) // 10])
		median_mhtn_list.append(median(mhtn_list))
		
		mean_euclid_list.append(mean(euclid_list))
		stdev_euclid_list.append(stdev(euclid_list))
	
	return quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		   active_share_euclid_list, active_share_euclid_ex_cash_list, \
		   median_mhtn_list, mhtn_10_list, mhtn_90_list, \
		   median_euclid_list, euclid_10_list, euclid_90_list, \
		   mean_euclid_list, stdev_euclid_list


def create_time_series_panel(date_range):
	index_name = 'S&P 500 TR USD'
	
	quarter_end_list, active_share_mhtn_list, active_share_euclid_list, median_mhtn_list, mhtn_10_list, mhtn_90_list, \
	median_euclid_list, euclid_10_list, euclid_90_list = load_data(index_name, date_range)
	
	S_and_P_active_share_series_plot = draw_active_share_time_series(
		date_range, index_name, median_mhtn_list, mhtn_10_list, mhtn_90_list, median_euclid_list, euclid_10_list,
		euclid_90_list)
	
	index_name = 'Russell 2000 TR USD'
	quarter_end_list, active_share_mhtn_list, active_share_euclid_list, median_mhtn_list, mhtn_10_list, mhtn_90_list, \
	median_euclid_list, euclid_10_list, euclid_90_list = load_data(index_name, date_range)
	
	Russel_2000_active_share_series_plot = draw_active_share_time_series(
		date_range, index_name, median_mhtn_list, mhtn_10_list, mhtn_90_list, median_euclid_list, euclid_10_list,
		euclid_90_list)
	
	plot = row(S_and_P_active_share_series_plot, Russel_2000_active_share_series_plot)
	
	show(plot)
	export_png(plot, filename="active_share_time_series.png")
	
	return


def create_histogram_panel(date_range):
	index_name = 'S&P 500 TR USD'
	
	quarter_end_list, active_share_mhtn_list, active_share_euclid_list, median_mhtn_list, mhtn_10_list, mhtn_90_list, \
	median_euclid_list, euclid_10_list, euclid_90_list = load_data(index_name, date_range)
	
	euclid_histogram_plot = draw_histogram(active_share_euclid_list, is_euclid=True)
	
	mhtn_histogram_plot = draw_histogram(active_share_mhtn_list, is_euclid=False)
	
	histogram_plot = row(euclid_histogram_plot, mhtn_histogram_plot)
	
	show(histogram_plot)
	export_png(histogram_plot, filename="active_share_histograms.png")
	
	return


if __name__ == '__main__':
	
	# set up date_range
	#a=numpy.array([2.0,4.0])
	#print(a*2)
	#exit()
	#b=numpy.array([2,4])
	#print(a,b)
	#print(numpy.divide(a,b))
	#exit();
	
	
	end_date = date(2007, 12, 31)
	date_range = [end_date]
	
	for i in range(11 * 4):
		date_range.append(change_to_another_month_end(end_date, 3 * (i + 1)))
	
	print(date_range)
	benchmark_list = ['Russell 3000 TR USD',
					  'Russell Mid Cap TR USD', 'Russell Mid Cap Value TR USD', 'Russell Mid Cap Growth TR USD',
					  'Russell 1000 TR USD', 'Russell 1000 Growth TR USD', 'Russell 1000 Value TR USD',
					  'Russell 2000 TR USD', 'Russell 2000 Growth TR USD', 'Russell 2000 Value TR USD',
					  'S&P 500 TR USD']
	
	index_name = benchmark_list[-1]
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, active_share_euclid_list, active_share_euclid_ex_cash_list, \
	median_mhtn_list, mhtn_10_list, mhtn_90_list, \
	median_euclid_list, euclid_10_list, euclid_90_list, \
	mean_euclid_list, stdev_euclid_list = load_data(index_name, date_range)
	
	D1_array = numpy.array(active_share_mhtn_ex_cash_list)*2
	result = numpy.divide(D1_array, active_share_euclid_ex_cash_list)
	result = numpy.power(result,2)*0.79788456
	print(numpy.mean(result), numpy.std(result))
	exit()
	
	# create_time_series_panel(date_range)
	
	# create_histogram_panel(date_range)
	
	print(mean_euclid_list)
	
	print(stdev_euclid_list)
	
	data_array = numpy.array(active_share_euclid_ex_cash_list)
	
	N = 50
	data_array_2 = (data_array / 100) * 0.79788456 * N ** 0.5
	
	chi_max_likelihood = ChiMaxLikelihood(data_array)
	
	k_solved, sigma_solved = chi_max_likelihood.solve_k_sigma(k_guess=4)
	
	print('solved', k_solved, sigma_solved)
	k = k_solved
	sigma = sigma_solved
	# plot_euclid=draw_active_share_histogram(data_array, k, sigma, bins="auto", density_histogram=False)
	# show(plot_euclid)
	
	# check sigma
	print((k * sigma ** 2) ** 0.5)
	
	data_array = numpy.array(active_share_mhtn_ex_cash_list)
	
	data_array = data_array / 100
	
	chi_max_likelihood = ChiMaxLikelihood(data_array)
	
	k_solved, sigma_solved = chi_max_likelihood.solve_k_sigma(k_guess=4)
	
	print('solved', k_solved, sigma_solved)
	k = k_solved
	sigma = sigma_solved
	plot_mhtn = draw_active_share_histogram(data_array, data_array_2, k, sigma, bins="auto", density_histogram=False)
	# show(row(plot_euclid, plot_mhtn))
	show(plot_mhtn)
	
	exit()
	chi_ks_test = ChiKSTest(data_array)
	
	k_solved, sigma_solved = chi_ks_test.solve_k_sigma(k_guess=k_solved, sigma_guess=sigma_solved)
	
	print('solved', k_solved, sigma_solved)
	k = k_solved
	sigma = sigma_solved
	plot = draw_active_share_histogram(data_array, k, sigma, bins="auto", density_histogram=False)
	show(plot)
	
	# check sigma
	print((k * sigma ** 2) ** 0.5)
