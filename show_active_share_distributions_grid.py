from fundskill_utilities.setup_python_file_with_django import *  # this sets up the django environment

import numpy
from datetime import datetime, date
from statistics import median, stdev, mean
from scipy.stats import shapiro
import csv

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d

from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, LinearAxis, Title, PrintfTickFormatter, NumeralTickFormatter

from bokeh.models.tickers import FixedTicker
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead, LabelSet
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource, Div
from bokeh.layouts import row, gridplot, column, Spacer
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


def load_data_for_distributions(index_name, date_range):
	""" Load orginal data and calcuate quarterly statistics
	:param index_name:
	:param date_range:
	:return:
	"""
	
	results_file_name = index_name + '_active_share.csv'
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
	active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, _ \
		= load_data_from_csv_file(results_file_name)
	
	# Calculate mean concentration index of benchmark
	for quarter_end_date in date_range:
		
		concentration_list = []
		
		for idx in range(len(quarter_end_list)):
			
			if quarter_end_date == quarter_end_list[idx]:
				concentration = benchmark_concentration_list[idx]
				continue
		
		concentration_list.append(concentration)
	
	benchmark_concentration_average = mean(concentration_list)
	
	return benchmark_concentration_average, active_share_euclid_list, active_share_mhtn_list


def draw_histogram_for_grid(active_share_list, is_euclid=True, add_title=False, add_side_title=False, is_S_and_P=False):
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
	plot = figure(plot_width=int(320), plot_height=200)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	font = "10pt"
	"""if add_title is True:
		if is_euclid:
			my_title_text = "Euclidean Active Share"
		else:
			my_title_text = "Manhattan Active Share"
		
		my_title = Title(text=my_title_text, align='center',
						 text_font_size="14pt", standoff =10,
						 text_line_height=1, vertical_align='middle')
		plot.add_layout(my_title, "above")"""
	
	if add_side_title:
		if is_S_and_P:
			my_side_title_text = 'S&P 500'
		else:
			my_side_title_text = 'Russell 2000'
		
		my_side_title = Title(text=my_side_title_text, align='center',
							  text_font_size="14pt",
							  text_line_height=1, vertical_align='middle')
		
		plot.add_layout(my_side_title, "left")
	
	if is_euclid:
		plot.x_range = Range1d(0.0, 40)
	else:
		plot.x_range = Range1d(0.0, 110)
	plot.xaxis.axis_label = ' '
	plot.xaxis[0].formatter = PrintfTickFormatter(format=" %u%%")
	plot.xaxis[0].major_label_text_align = "right"
	
	plot.xaxis[0].ticker.desired_num_ticks = 2
	plot.min_border_right = 20
	plot.min_border_bottom = 30
	
	plot.yaxis.axis_label = ' Relative Frequency'
	plot.yaxis[0].formatter = NumeralTickFormatter(format="0%")
	plot.yaxis[0].ticker.desired_num_ticks = 4
	plot.y_range = Range1d(0.0, max(frequency_list) + 0.005)
	plot.yaxis.minor_tick_line_color=None
	if is_S_and_P:
		plot.y_range = Range1d(0.0, 0.050)
	else:
		if is_euclid:
			plot.y_range = Range1d(0.0, 0.0801)
		else:
			plot.y_range = Range1d(0.0, 0.1501)
	
	
	plot.axis.axis_label_text_font_size = '10pt'
	# plot.xaxis.axis_label_text_font = font
	# plot.yaxis.axis_label_text_font = font
	
	plot.axis.major_label_text_font_size = font
	# plot.xaxis.major_label_text_font = font
	# plot.yaxis.major_label_text_font = font
	
	if is_euclid:
		label_text = "\\mathbf{ A_{\\mathrm{Euclid}}}"
		x_position = 21
		plot.xaxis.axis_label = r"$$\mathbf{ A_{\mathrm{Euclid}}}$$"
		plot.xaxis.axis_label_standoff=0
	else:
		label_text = "\\mathbf{ A_{\\mathrm{Mhtn}}}"
		x_position = 50
		plot.xaxis.axis_label = r"$$\mathbf{ A_{\mathrm{Mhtn}}}$$"
	
	latex_x_axis_label = LatexLabel(
		text=label_text,
		x=x_position,
		y=-0.0035,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size=double_graph_latex_label_font_size,
		background_fill_alpha=1)
	
	# plot.add_layout(latex_x_axis_label)
	
	# construct histogram
	r0 = plot.quad(
		bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
		fill_color='lightgrey', line_color='black')  # legend='Underperforming monkey portfolios')
	
	return plot


if __name__ == '__main__':
	
	# set up date_range and benchmark_list
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	# only dealing with two benchmarks
	benchmark_list = [ 'S&P 500 TR USD','Russell 2000 TR USD', ]
	
	plot_euclid={}
	plot_mhtn={}
	
	for i, index_name in enumerate(benchmark_list):
	
		benchmark_concentration_average, active_share_euclid_list, active_share_mhtn_list = \
			load_data_for_distributions(index_name, date_range)
		print('************',i)
		if i==0:
			add_title=True
			is_S_and_P= True
		else:
			add_title=False
			is_S_and_P = False
			
		plot_euclid[i] = draw_histogram_for_grid(active_share_euclid_list, is_euclid=True, add_title=add_title, add_side_title=True, is_S_and_P=is_S_and_P)
		plot_mhtn[i] = draw_histogram_for_grid(active_share_mhtn_list, is_euclid = False, add_title = add_title,add_side_title=False, is_S_and_P=is_S_and_P )
	
	# heading fills available width
	heading_euclidean = Div(text='<b>Euclidean Active Share</b>',
							style={'font-size': '15pt', 'color': 'black', 'font-style':  'bold'}, height=30,  align='end', margin=(0,15,5,0))
	heading_mhtn = Div(text='<b>Manhattan Active Share</b>', style={'font-size': '15pt', 'color': 'black'}, height=30,  align='start',margin=(0,0,5,60) )
	
	first_column = column(heading_euclidean, plot_euclid[0],Spacer(height=10), plot_euclid[1])
	
	second_column = column(heading_mhtn, plot_mhtn[0],Spacer(height=10), plot_mhtn[1])
	
	#grid = gridplot([[plot_euclid[0], plot_mhtn[0]], [plot_euclid[1], plot_mhtn[1]]],width=320, height=200, toolbar_location=None, toolbar_options={'logo': None})
	
	grid_plot =(row(first_column, second_column))
	
	show(grid_plot)
	
	export_png(grid_plot, filename="show_active_share_distributions_grid_plot.png")