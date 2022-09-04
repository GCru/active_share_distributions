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


def positions_vs_concentration_scatter_plot(title_text, benchmark_concentration_list, mean_number_of_positions):
	
	# Set up plot
	plot = figure(plot_width=int(500), plot_height=500)
	plot.toolbar.logo = None
	plot.toolbar_location = None
	
	my_title = Title(text=title_text, align='center',
					 text_font=font, text_font_size=double_graph_title_font_size,
					 text_line_height=1, vertical_align='middle')
	plot.add_layout(my_title, "above")
	
	#if index_name == 'S&P 500':
	plot.x_range = Range1d(0.0, 0.2)
	plot.y_range = Range1d(100, 900)
	#else:
	#	plot.x_range = Range1d(0.0, 2500)
	#	plot.y_range = Range1d(0.0, 4000)
	
	plot.xaxis.axis_label = 'Benchmark concentration index'
	plot.xaxis[0].formatter = NumeralTickFormatter(format="0%")
	
	# plot.xaxis[0].formatter = NumeralTickFormatter(format="0,0")
	# plot.min_border_right = 20
	# plot.min_border_bottom = 30
	
	plot.yaxis.axis_label = title_text
	
	# plot.y_range = Range1d(0.0, 0.08)
	
	plot.axis.axis_label_text_font_size = "22px" #double_graph_axis_label_font_size
	plot.xaxis.axis_label_text_font = font
	plot.yaxis.axis_label_text_font = font
	
	plot.axis.major_label_text_font_size = "18px" #double_graph_major_label_font_size
	plot.xaxis.major_label_text_font = font
	plot.yaxis.major_label_text_font = font
	
	# construct histogram
	plot.circle(benchmark_concentration_list, mean_number_of_positions, size=2,
				color='gray')
	
	# show(plot)
	
	return plot


if __name__ == '__main__':
	
	
	# set up date_range and benchmark_list
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	benchmark_concentration_list =[]
	mean_euclid_active_share = []
	stdev_euclid_active_share = []
	mean_mhtn_active_share = []
	stdev_mhtn_active_share = []
	
	mean_number_of_implied_positions = []
	stdev_number_of_implied_positions = []
	
	mean_number_of_actual_positions = []
	stdev_number_of_actual_positions = []
	
	overall_benchmark_concentration_list = []
	overall_active_share_euclid_list = []
	overall_active_share_mhtn_list = []
	
	
	for benchmark in benchmark_list:
		
		filename= benchmark+'_active_share.csv'
		quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
			active_share_euclid_list, active_share_euclid_ex_cash_list, all_benchmark_concentration_list,\
				all_actual_number_of_active_positions_list = load_data_from_csv_file(filename)
	
		for quarter_date in date_range:
			
			mhtn_list =[]
			euclid_list = []
			implied_number_of_positions_list = []
			actual_number_of_positions_list = []
			for count, item_date in enumerate(quarter_end_list):
				
				if item_date == quarter_date:
					
					mhtn_list.append(active_share_mhtn_list[count])
					euclid_list.append(active_share_euclid_list[count])
					
					actual_number_of_positions_list.append(all_actual_number_of_active_positions_list[count])
					
					implied_number_of_positions_list.append( (((mhtn_list[-1] * 2)/euclid_list[-1])* (numpy.pi / 2))**2 )
					
					benchmark_concentration = all_benchmark_concentration_list[count]
					
					
			benchmark_concentration_list.append(benchmark_concentration/100)
			
			mean_euclid_active_share.append(numpy.mean(euclid_list))
			stdev_euclid_active_share.append(numpy.std(euclid_list))
			
			mean_mhtn_active_share.append(numpy.mean(mhtn_list))
			stdev_mhtn_active_share.append(numpy.std(mhtn_list))
			
			mean_number_of_implied_positions.append(numpy.mean(implied_number_of_positions_list))
			stdev_number_of_implied_positions.append(numpy.std(implied_number_of_positions_list))
			
			mean_number_of_actual_positions.append(numpy.mean(actual_number_of_positions_list))
			stdev_number_of_actual_positions.append(numpy.std(actual_number_of_positions_list))
			
			overall_active_share_euclid_list = overall_active_share_euclid_list +active_share_euclid_list
			overall_active_share_mhtn_list  = overall_active_share_mhtn_list +active_share_mhtn_ex_cash_list
			overall_benchmark_concentration_list = overall_benchmark_concentration_list +all_benchmark_concentration_list
			
	zipped_list = zip(benchmark_concentration_list, mean_number_of_actual_positions, mean_number_of_implied_positions)
			
	sorted_lists = sorted(zipped_list)
	
	benchmark_concentration_list, mean_number_of_actual_positions, mean_number_of_implied_positions = zip(*sorted_lists)
		
	p1 = positions_vs_concentration_scatter_plot('Actual mean active position counts', benchmark_concentration_list, mean_number_of_actual_positions)
	
	p2 = positions_vs_concentration_scatter_plot('Modelled mean active positions counts', benchmark_concentration_list,
												 mean_number_of_implied_positions)
	
	plot=row(p1, Spacer(width=15),p2)
	
	show(plot)
	
	export_png(plot, filename="number_of_active_positions_vs_concentration_plot.png")
	