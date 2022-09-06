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


def setup_date_range_and_benchmark_list():
	"""Sets quarter ends and the benchmarks to use. Benchmarks are ordered from lowest to highest concentration index"""

	end_date = date(2007, 12, 31)
	date_range = [end_date]

	for i in range(14 * 4):
		date_range.append(change_to_another_month_end(end_date, 3 * (i + 1)))

	benchmark_list = ['Russell 2000 TR USD', 'Russell 2000 Value TR USD',
				  'Russell Mid Cap TR USD', 'Russell 2000 Growth TR USD',
				  'Russell Mid Cap Value TR USD', 'Russell Mid Cap Growth TR USD',
				  'Russell 3000 TR USD', 'Russell 1000 TR USD', 'S&P 500 TR USD',
				   'Russell 1000 Value TR USD','Russell 1000 Growth TR USD',
				  ]

	return date_range, benchmark_list

def load_data_from_csv_file(file_name):
	active_share_mhtn_list = []
	active_share_mhtn_ex_cash_list = []
	active_share_euclid_list = []
	active_share_euclid_ex_cash_list = []
	nr_active_weights = []
	quarter_end_list = []
	benchmark_concentration_list = []
	
	with open(file_name, mode='r') as file:
		# reading the CSV file
		csv_file = csv.DictReader(file)
		
		# displaying the contents of the CSV file
		for line in csv_file:
			quarter_end_str = line['quarter_end']
			#print(quarter_end_str)
			quarter_end_date = datetime.datetime.strptime(quarter_end_str, '%b%Y')
			quarter_end_date = change_to_month_end(quarter_end_date)
			quarter_end_list.append(quarter_end_date)
			
			active_share_mhtn_list.append(float(line['active_share_mhtn']))
			active_share_mhtn_ex_cash_list.append(float(line['active_share_mhtn_ex_cash']))
			active_share_euclid_list.append(float(line['active_share_euclid']))
			active_share_euclid_ex_cash_list.append(float(line['active_share_euclid_ex_cash']))
			benchmark_concentration_list.append(float(line['benchmark_concentration']))
			nr_active_weights.append(float(line['nr_active_weights']))
	
	return quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
		   active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, nr_active_weights






if __name__ == '__main__':
	
	date_range, _=setup_date_range_and_benchmark_list()
	
	print(date_range)
	
	print('Done')