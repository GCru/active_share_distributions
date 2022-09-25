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

from make_histogram_procedure import make_histogram
from chi_distribution_plot_old import ChiMaxLikelihood, draw_active_share_histogram, ChiKSTest

from shared_functions import load_data_from_csv_file


def draw_position_histogram(position_list, index_name='S\&P 500'):
	
	frequency_list, bin_edges_list = make_histogram(position_list)
	
	left_edges = bin_edges_list[:-1]
	right_edges = bin_edges_list[1:]
	data = {'frequency': frequency_list, 'left_edges': left_edges, 'right_edges': right_edges}
	source = ColumnDataSource(data=data)
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	if index_name=='S\&P 500':
		my_title = "S\&P 500"
	else:
		my_title = "To be confoirmed"
	
	my_title = Title(text=my_title, align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")
	
	plot.x_range = Range1d(0.0, right_edges[-1])
	plot.xaxis.axis_label = ' '
	plot.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
	plot.min_border_right = 20
	plot.min_border_bottom = 30
	
	plot.yaxis.axis_label = 'Relative Frequency'
	plot.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	plot.y_range = Range1d(0.0, 0.08)
	
	plot.axis.axis_label_text_font_size = double_graph_axis_label_font_size
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font
	
	plot.axis.major_label_text_font_size = double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	
	"""if is_euclid:
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
	
	plot.add_layout(latex_x_axis_label)"""
	
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='lightgrey', line_color='black')  # legend='Underperforming monkey portfolios')
	
	return plot


"""
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
"""

if __name__ == '__main__':
	
	# set up date_range
	# a=numpy.array([2.0,4.0])
	# print(a*2)
	# exit()
	# b=numpy.array([2,4])
	# print(a,b)
	# print(numpy.divide(a,b))
	# exit();
	
	end_date = date(2007, 12, 31)
	date_range = [end_date]
	
	for i in range(11 * 4):
		date_range.append(change_to_another_month_end(end_date, 3 * (i + 1)))
		
		# benchmarks in order of concentration indices
		benchmark_list = [
			'Russell 2000 TR USD', 'Russell 2000 Value TR USD', 'Russell Mid Cap TR USD',
			'Russell 2000 Growth TR USD', 'Russell Mid Cap Value TR USD', 'Russell Mid Cap Growth TR USD',
			'Russell 3000 TR USD', 'Russell 1000 TR USD', 'Russell 1000 Growth TR USD', 'Russell 1000 Value TR USD',
			'S&P 500 TR USD', 'Russell 2000 Value TR USD', 'Russell 2000 Growth TR USD']
	
	index_name = benchmark_list[-3]
	results_file_name = index_name + '_active_share.csv'

	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		   active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, \
			number_of_active_positions_list = load_data_from_csv_file(results_file_name)
	
	D1_array = numpy.array(active_share_mhtn_ex_cash_list) * 2
	result = numpy.divide(D1_array, active_share_euclid_ex_cash_list)*(numpy.pi/2)
	implied_number_of_active_positions_array = numpy.power(result, 2)
	print(numpy.mean(implied_number_of_active_positions_array), numpy.std(implied_number_of_active_positions_array))
	
	plot=draw_position_histogram(implied_number_of_active_positions_array)
	#show(plot)
	
	#plot = draw_active_share_histogram(result, k, sigma, bins="auto", density_histogram=False)
	#show(plot)
	
	# check sigma
	#print((k * sigma ** 2) ** 0.5)
	
	actual_number_of_active_positions_array = numpy.array(number_of_active_positions_list)
	
	scatter_plot = figure(plot_width=int(500), plot_height=500)
	
	scatter_plot.circle(actual_number_of_active_positions_array, implied_number_of_active_positions_array, size=2)
	show(scatter_plot)
