from fundskill_utilities.setup_python_file_with_django import *  # this sets up the django environment

import numpy
from datetime import date, datetime
from statistics import median, stdev
from scipy.stats import linregress, shapiro
import csv

from math import isnan

from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d, PrintfTickFormatter, NumeralTickFormatter

from fundskill.global_data_settings import FUNDSKILL_START_DATE, FUNDSKILL_END_DATE, \
	MIN_QUALIFYING_NET_EQUITY_WEIGHT_FOR_RANKING
from fundskill_utilities.fundskill_utilities import change_to_next_month_end, change_to_another_month_end, \
	change_to_month_end, change_to_quarter_end, index, change_to_year_end
from core.models import *

#from active_risk_conventional_routines import load_stock_returns_in_return_dictionary_old, set_up_numpy_arrays, \
#	calculate_active_share_and_risk, get_benchmark_stdevs_old

from  calculate_active_risk import get_benchmark_stdevs, load_stock_returns_in_return_dictionary, \
	calculate_active_share, setup_and_calculate_active_risk

from get_active_tickers_and_weights_procedure import get_active_tickers_and_weights

from shared_functions import setup_date_range_and_benchmark_list


def is_fund_active_weights_from_normal(active_weight_dict):
	
	# put all the active weights in a list
	active_weights_list = list(active_weight_dict.values())
	max_positon = max([abs(item) for item in active_weights_list])
	
	active_weights_list = [item for item in active_weights_list if abs(item) > 0.025 * max_positon]
	p_all = shapiro(active_weights_list)
	
	active_weights_adjusted_list = [item for item in active_weights_list if abs(item)>0.05*max_positon]
	
	p_ex_small = shapiro(active_weights_adjusted_list)
	
	return p_all.pvalue, p_ex_small.pvalue, len(active_weights_list), len(active_weights_adjusted_list)
	

def calculate_active_share_and_write_to_file(benchmark_name, date_range, active_share_file_name):
	results_list = []
	
	# get active weights
	for quarter_end in date_range:
		print(quarter_end)
		quarter_end_str = quarter_end.strftime("%b%Y")
		# load benchmark
		
		benchmark = Benchmark.objects.get(name=benchmark_name)
		try:
			benchmark_holdings = BenchmarkHoldings.objects.get(benchmark=benchmark, date=quarter_end)
		except:
			print('No data for: ', quarter_end)
			continue
		
		benchmark_concentration = benchmark_holdings.concentration_score()
		
		# load funds
		funds_queryset = MutualFund.objects.filter(benchmark=benchmark)
		
		for fund in funds_queryset.iterator():
			
			try:
				fund_holdings = FundHoldings.objects.get(mutual_fund=fund, date=quarter_end)
			except:
				continue
			
			# skip all funds for which not 85% to 100% of weights is in equities and also funds with short positions
			if sum(fund_holdings.weights) > 100 or sum(fund_holdings.weights) < 85:
				print(quarter_end_str, fund.name, fund.id, 'Sum of positions does not qualify ',
					  sum(fund_holdings.weights))
				continue
			
			# skip all funds with short positions
			skip = False
			for w in fund_holdings.weights:
				if w < 0:
					skip = False #True
			if skip:
				print(quarter_end_str, fund.name, fund.id, 'Short positions, does not qualify ')
				continue
			
			print()
			print(quarter_end_str, fund.name, fund.id, 'with benchmark', benchmark.name)
			
			results_dict = {
				'quarter_end': quarter_end_str,
				'fund_name': fund.name,
				'benchmark_concentration': benchmark_concentration, }
			# 'cross_sect_stan_dev': cross_sect_stan_dev,
			# 'cross_sect_skew': cross_sect_skew,
			# 'cross_sect_kurt': cross_sect_kurt}
			
			active_weight_dict = get_active_tickers_and_weights(fund_holdings, benchmark_holdings)
			
			p_all, p_ex_small, nr_active_weights, nr_active_weights_ex_small = is_fund_active_weights_from_normal(active_weight_dict)
			results_dict.update({'p_value_all': p_all,
								 'p_value_ex_small': p_ex_small,
								 'nr_active_weights': nr_active_weights,
								 'nr_active_weights_ex_small': nr_active_weights_ex_small })
			
			
			active_share_euclid, active_share_mhtn = calculate_active_share(active_weight_dict)
			print('Active shares', active_share_euclid, active_share_mhtn)
			
			results_dict.update({'active_share_mhtn': active_share_mhtn,
									 'active_share_euclid': active_share_euclid})
			
			active_share_euclid, active_share_mhtn = calculate_active_share(active_weight_dict, with_cash=False)
			
			results_dict.update({'active_share_mhtn_ex_cash': active_share_mhtn,
								 'active_share_euclid_ex_cash': active_share_euclid})
			
			
			results_list.append(results_dict)
			
	
	# save in csv file
	
	field_names = ['quarter_end', 'fund_name', 'active_share_euclid', 'active_share_mhtn',
				   'active_share_euclid_ex_cash', 'active_share_mhtn_ex_cash',
				   'benchmark_concentration', 'p_value_all', 'nr_active_weights',
				   'p_value_ex_small', 'nr_active_weights_ex_small' ]
	
	with open(active_share_file_name, 'w', newline='') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=field_names)
		writer.writeheader()
		writer.writerows(results_list)


def find_benchmarks_with_enough_data():
	b_qset = Benchmark.objects.all()
	
	date_from = date(2007, 12, 31)
	date_to = date(2020, 12, 31)
	
	for b in b_qset:
		
		funds_with_holdings = 0
		mutual_fund_qset = MutualFund.objects.filter(benchmark=b)
		
		for m in mutual_fund_qset:
			funds_with_holdings = funds_with_holdings + \
								  FundHoldings.objects.filter(mutual_fund=m, date__gte=date_from,
															  date__lte=date_to).count()
		if funds_with_holdings > 2000:
			b_holdings = BenchmarkHoldings.objects.get(benchmark=b, date=date_to)
			print(b.name, b_holdings.concentration_score(), funds_with_holdings)


if __name__ == '__main__':
	
	# set up date_range
	
	date_range, benchmark_list = setup_date_range_and_benchmark_list()
	
	for benchmark_name in benchmark_list:
		active_share_file_name = benchmark_name + '_' + 'active_share' + '.csv'
		
		calculate_active_share_and_write_to_file(benchmark_name, date_range, active_share_file_name)
