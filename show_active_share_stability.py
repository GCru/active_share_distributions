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
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead, LabelSet, Whisker
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
from shared_functions import load_data_from_csv_file, setup_date_range_and_benchmark_list

def load_data_for_stability(index_name, date_range):
	""" Load orginal data and calcuate quarterly statistics
	:param index_name:
	:param date_range:
	:return:
	"""
	
	results_file_name = index_name + '_active_share.csv'
	
	quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, _\
			= load_data_from_csv_file(results_file_name)
	
	print('Number of data points for ', index_name, ':',len(quarter_end_list))
	mean_quarterly_euclid_list = []
	
	mean_quarterly_mhtn_list = []
	concentration_list = []
	# Calculate ranges and mean and median for each quarter end
	for quarter_end_date in date_range:
		
		euclid_list = []
		mhtn_list = []
		
		
		for idx in range(len(quarter_end_list)):
			
			if quarter_end_date == quarter_end_list[idx]:
				euclid_list.append(active_share_euclid_list[idx])
				mhtn_list.append(active_share_mhtn_list[idx])
				concentration = benchmark_concentration_list[idx]
		
		mean_quarterly_euclid_list.append(mean(euclid_list))
		mean_quarterly_mhtn_list.append(mean(mhtn_list))
		concentration_list.append(concentration)
	
	euclid_average = mean(mean_quarterly_euclid_list)
	euclid_stdev = stdev(mean_quarterly_euclid_list)
	euclid_low = min(mean_quarterly_euclid_list)
	euclid_high = max(mean_quarterly_euclid_list)
	
	mhtn_average = mean(mean_quarterly_mhtn_list)
	mhtn_stdev = stdev(mean_quarterly_mhtn_list)
	
	bendhmark_concentration_average = mean(concentration_list)
	
	return euclid_average, euclid_low, euclid_high, euclid_stdev, mhtn_average,mhtn_stdev, bendhmark_concentration_average




if __name__ == '__main__':
	
	# set up date_range and benchmark_list
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	index_name_list=[]
	euclid_average_list = []
	euclid_stdev_list = []
	euclid_low_list = []
	euclid_high_list =[]
	
	mhtn_average_list = []
	
	for index_name in benchmark_list:
		euclid_average,  euclid_low,euclid_high, euclid_stdev,mhtn_average, mhtn_stdev, benchmark_concentration_average \
			= load_data_for_stability(index_name, date_range)
	
		print(index_name, benchmark_concentration_average,euclid_average, euclid_stdev, mhtn_average, mhtn_stdev )
		
		index_name_list.append(index_name[0:index_name.find('TR')] + '(' + str(round(benchmark_concentration_average,1))+'%)')
		euclid_average_list.append(euclid_average)
		euclid_stdev_list.append(euclid_stdev)
		euclid_low_list.append(euclid_low)
		euclid_high_list.append(euclid_high)
		
		mhtn_average_list.append(mhtn_average)
		
	print('Min and maximum Eucild', min(euclid_average_list), max(euclid_average_list))
	print('Min and maximum Manhattan', min(mhtn_average_list), max(mhtn_average_list))
	
	
	y_values = [i for i in range(len(index_name_list))]
	
	data = {'y_values': index_name_list,
			'euclid_averages': euclid_average_list,
			'upper': euclid_high_list, #[euclid_average_list[i]+ euclid_stdev_list[i] for i in range(len(euclid_average_list))],
			'lower': euclid_low_list, #[euclid_average_list[i] - euclid_stdev_list[i] for i in range(len(euclid_average_list))],
			'mhtn_averages': mhtn_average_list}
	
	print([euclid_average_list[i] + euclid_stdev_list[i] for i in range(len(euclid_average_list))])
	
	source = ColumnDataSource(data=data)
	
	p = figure(y_range = index_name_list, width=640, height=400)
	
	my_title = Title(text='Average active shares of US mutual funds', text_font=font, text_font_size=double_graph_title_font_size,
					 align='center', text_line_height=1, vertical_align='middle')
	
	#label_euclidean = Label(x=68, y=110, #x_units='screen', y_units='screen',
	#				 text='Euclidean active share', #render_mode='css',
	#				 border_line_color=None, border_line_alpha=1.0, angle=90, angle_units ="deg",
	#				 background_fill_color=None, background_fill_alpha=1.0)
	
	label_euclidean = Label(x=5.7, y=4.0,  # x_units='screen', y_units='screen',
							text='Euclidean active share', text_font_style ='normal', # render_mode='css',
							border_line_color=None, border_line_alpha=1.0, angle=90, angle_units="deg",
							background_fill_color=None, background_fill_alpha=1.0)
	
	
	p.add_layout(label_euclidean)
	
	arrow_euclidean = Arrow(end=NormalHead(fill_color="black", size=10),
                   x_start=5, y_start=3.5, x_end=5, y_end=1.5)
	p.add_layout(arrow_euclidean)
	
	#label_mhtn = Label(x=338, y=40, x_units='screen', y_units='screen',
	#						text='Manhattan active share', render_mode='css',
	#						border_line_color=None, border_line_alpha=1.0, angle=90, angle_units="deg",
	#						background_fill_color=None, background_fill_alpha=1.0)
	
	label_mhtn = Label(x=28.2, y=1.5,
					   text='Manhattan active share', text_font_style='normal',
					   border_line_color=None, border_line_alpha=1.0, angle=90, angle_units="deg",
					   background_fill_color=None, background_fill_alpha=1.0)
	
	p.add_layout(label_mhtn)
	
	arrow_mhtn = Arrow(end=NormalHead(fill_color="black", size=10),
							x_start=27.5, y_start=7.75, x_end=27.5, y_end=9.75)
	p.add_layout(arrow_mhtn)
	
	p.min_border_right =20

	p.toolbar.logo = None
	p.toolbar_location = None
	
	p.x_range = Range1d(0,40)
	
	p.add_layout(
		Whisker(source=source, base='y_values', upper="upper", lower="lower", dimension="width", line_color='black',level='overlay'))
	
	p.hbar(y= 'y_values', height=0.5, left=0,
		   right='euclid_averages', color="lightgray", source=source)
	
	p.yaxis.major_label_text_font_size = "10pt"
	p.xaxis.major_label_text_font_size = "10pt"
	
	p.xaxis.minor_tick_line_color = None
	p.xaxis.major_label_overrides = {20: '', 25: '', 30: '', 35: '', 40: ''}
	p.xaxis[0].formatter = PrintfTickFormatter(format="%u%%")
	
	p.extra_x_ranges = {'MhtnRange':Range1d(50,90)}
	p.add_layout(LinearAxis(x_range_name="MhtnRange", minor_tick_line_color=None, major_label_text_font_size='10pt',
							major_label_overrides={50:'', 55: '', 60: '', 65:''},formatter = PrintfTickFormatter(format="%u%%")),'above')
	
	p.circle(x='mhtn_averages', y='y_values', source=source, x_range_name = 'MhtnRange', size=7.5, color='dimgray')
	
	p.add_layout(my_title, 'above')

	
	show(p)
	
	export_png(p, filename="show_active_share_stability_plot.png")
	