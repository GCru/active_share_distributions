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

#from fundskill_utilities.fundskill_shared_bokeh_utilities import HistogramPlot, setup_date_ticker_ju

from bokeh_constants import *

#from shared_with_active_risk_paper import make_histogram
from chi_distribution_plot_old import ChiMaxLikelihood, draw_active_share_histogram, ChiKSTest


from shared_functions import load_data_from_csv_file, setup_date_range_and_benchmark_list

if __name__ == '__main__':
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	combined_cash_list = []
	
	for benchmark_name in benchmark_list:
	
	
		results_file_name = benchmark_name + '_active_share.csv'
	
		quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
			active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, \
			number_of_active_positions_list = load_data_from_csv_file(results_file_name)
		
		cash_list = [((active_share_euclid_list[i]/100)**2 - (active_share_euclid_ex_cash_list[i]/100)**2)**0.5
					 for i in range(len(quarter_end_list))]
		
		combined_cash_list = combined_cash_list +cash_list
		
		print(benchmark_name, numpy.mean(cash_list), numpy.std(cash_list) )
	
	print('Overall', numpy.mean(combined_cash_list), numpy.std(combined_cash_list))