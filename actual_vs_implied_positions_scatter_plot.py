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
from bokeh.layouts import row, Spacer
from bokeh.io import export_png

from math import pi

from latex_label_utility import LatexLabel
import datetime

from fundskill_utilities.fundskill_utilities import change_to_next_month_end, change_to_another_month_end, \
	change_to_month_end, change_to_quarter_end, index

from fundskill_utilities.fundskill_shared_bokeh_utilities import HistogramPlot, setup_date_ticker_jump

from bokeh_constants import *

from shared_with_active_risk_paper import make_histogram
from chi_distribution_plot_old import ChiMaxLikelihood, draw_active_share_histogram, ChiKSTest

from shared_functions import load_data_from_csv_file, setup_date_range_and_benchmark_list


def draw_scatter_plot(index_name='S&P 500'):
	
	# load data
	
	results_file_name = index_name + ' TR USD_active_share.csv'
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, \
		number_of_active_positions_list = load_data_from_csv_file(results_file_name)
	
	actual_number_of_active_positions_array = numpy.array(number_of_active_positions_list)
	
	# calculate implied number of active positions
	
	D1_array = numpy.array(active_share_mhtn_ex_cash_list) * 2
	result = numpy.divide(D1_array, active_share_euclid_ex_cash_list) * (numpy.pi / 2)
	implied_number_of_active_positions_array = numpy.power(result, 2)
	print(numpy.mean(implied_number_of_active_positions_array), numpy.std(implied_number_of_active_positions_array))
	

	# show(plot)
	
	# plot = draw_active_share_histogram(result, k, sigma, bins="auto", density_histogram=False)
	# show(plot)
	
	# check sigma
	# print((k * sigma ** 2) ** 0.5)
	

	
	
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	my_title = Title(text=index_name, align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")
	
	
	if index_name=='S&P 500':
		plot.x_range = Range1d(0.0, 1000)
		plot.y_range = Range1d(0.0,1400)
	else:
		plot.x_range = Range1d(0.0, 2500)
		plot.y_range = Range1d(0.0, 4000)
		
		
	plot.xaxis.axis_label = 'Actual number of active positions'
	#plot.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
	#plot.min_border_right = 20
	#plot.min_border_bottom = 30
	
	plot.yaxis.axis_label = 'Modelled number of active positions'
	#plot.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	#plot.y_range = Range1d(0.0, 0.08)
	
	print(double_graph_axis_label_font_size)
	plot.axis.axis_label_text_font_size = "22px" #double_graph_axis_label_font_size
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font
	
	plot.axis.major_label_text_font_size = double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	
	# construct histogram
	plot.circle(actual_number_of_active_positions_array, implied_number_of_active_positions_array, size=2,
				color='gray')
	
	
	#show(plot)
	
	return plot


if __name__ == '__main__':
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	p1 = draw_scatter_plot('S&P 500')
	
	p2= draw_scatter_plot('Russell 2000')
	
	panel_plot = row(p1,Spacer(width=10), p2)
	
	show(panel_plot)
	
	export_png(panel_plot, filename="actual_vs_implied_positions_scatter_plot.png")