import colorcet as cc
from numpy import linspace
from scipy.stats.kde import gaussian_kde

from bokeh.models import ColumnDataSource, FixedTicker, PrintfTickFormatter
from bokeh.plotting import figure, show
from bokeh.sampledata.perceptions import probly

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

from shared_functions import load_data_from_csv_file, setup_date_range_and_benchmark_list


def load_data_for_distributions(index_name, date_range):
    """ Load orginal data and calcuate quarterly statistics
	:param index_name:
	:param date_range:
	:return:
	"""
    
    results_file_name = index_name + '_active_share.csv'
    
    quarter_end_list, active_share_mhtn_list, active_share_mhtn_ex_cash_list, \
        active_share_euclid_list, active_share_euclid_ex_cash_list, benchmark_concentration_list, nr_of_active_weights \
            = load_data_from_csv_file(results_file_name)

    concentration_list = []
    # Calculate mean concentration index of benchmark
    for quarter_end_date in date_range:

        
        
        for idx in range(len(quarter_end_list)):
            
            if quarter_end_date == quarter_end_list[idx]:
                
                concentration = benchmark_concentration_list[idx]
                continue
                
                
        concentration_list.append(concentration)
    
    benchmark_concentration_average = mean(concentration_list)

    D1_array = numpy.array(active_share_mhtn_ex_cash_list) * 2
    implied_nr_of_active_weights = numpy.divide(D1_array, active_share_euclid_ex_cash_list) * (numpy.pi / 2)
    implied_nr_of_active_weights = numpy.power(implied_nr_of_active_weights, 2)
    
    return  benchmark_concentration_average, nr_of_active_weights, implied_nr_of_active_weights


def draw_ridge_graph(benchmark_list, date_range, actual_funds=False):
    benchmark_name_list = []
    
    mean_nr = []
    stdev_nr = []
    
    data_set = {}
    
    for benchmark in benchmark_list:
        benchmark_concentration_average, nr_of_active_weights, implied_nr_of_active_weights \
            = load_data_for_distributions(benchmark, date_range)
         
        if actual_funds:
            result = nr_of_active_weights
            scale =140
            title_text = 'Distributions of actual number of active positions'
        else:
            result= implied_nr_of_active_weights
            scale =240
            title_text = 'Distributions of modelled number of active positions'
            
        mean_nr.append(mean(result))
        stdev_nr.append(numpy.std(result))
        print('stdev', stdev_nr)
        benchmark_name = benchmark[0:benchmark.find('TR')] + '(' + str(round(benchmark_concentration_average, 1)) + '%)'
        
        data_set[benchmark_name] = result
        
        print(benchmark_name, benchmark_concentration_average, len(result), max(result))
        
        benchmark_name_list.append(benchmark_name)
    
    def ridge(category, data, scale=250):
        return list(zip([category] * len(data), scale * data))
    
    cats = benchmark_name_list
    
    palette = [cc.rainbow[i * 15] for i in range(17)]
    
    max_x = 1670
    
    x = linspace(-20, max_x, 5000)
    
    source = ColumnDataSource(data=dict(x=x))
    
    p = figure(y_range=cats, width=900, height = 900,
               x_range=(-12, max_x), toolbar_location=None)
    #p.min_border_right = 200
    
    # create grid
    for idx in range(100, max_x, 100):
        p.line([idx, idx], [0.5, 12], width=1, color='lightgray')
    
    for i, cat in enumerate(benchmark_name_list):
        pdf = gaussian_kde(data_set[cat])
        y = ridge(cat, pdf(x), scale=scale)
        source.add(y, cat)
        p.patch('x', cat, color='gray', alpha=1, line_color="black", source=source)
    
    p.outline_line_color = None
    p.background_fill_color = None
    
    p.xaxis.ticker = FixedTicker(ticks=list(range(0, 4001, 100)))
    p.xaxis.ticker.desired_num_ticks = 5
    p.xaxis.formatter = PrintfTickFormatter(format="%u")
    p.xaxis.fixed_location = 0.5
    p.xaxis.major_label_overrides = \
        {**{key: str(key) for key in range(0,1650,200)}, **{key: '' for key in range(100,1650,200)}}
    
    print()
    
    p.ygrid.grid_line_color = None
    
    p.xgrid.grid_line_color = "red"  # "#dddddd"
    p.xgrid.ticker = p.xaxis.ticker
    p.xgrid.bounds = (5, 12)
    p.xgrid.visible = False
    
    p.axis.minor_tick_line_color = None
    p.axis.major_tick_line_color = None
    p.axis.axis_line_color = 'black'
    
    p.xaxis.axis_line_color = None
    
    # does not work so add manually
    p.xaxis.axis_label = "Number of active positons"
    p.xaxis.axis_label_text_color = "black"
    x_axis_label = Label(x=500, y=-1.0, text="Number of active positions",
                       x_offset=5, y_offset=45, render_mode='canvas', text_font_size="14pt")
    #p.min_border_bottom= 100
    
    
    p.add_layout(x_axis_label)
    
    p.axis.major_label_text_font_size = graph_axis_label_font_size #'14pt' #graph_axis_label_font_size
   
    
    if actual_funds:
        p.y_range.range_padding = 0.12
    else:
        p.y_range.range_padding = 0.12

    for cat in range(0,11):
        mean_label = Label(x=1400, y=cat, text=str(round(mean_nr[cat])),
                      x_offset=5, y_offset=40.5, render_mode='canvas')
        
        mean_label.text_font_size = "12pt"
    
        p.add_layout(mean_label)
        
        stdev_label = Label(x=1500, y=cat, text=str(round(stdev_nr[cat])),
                      x_offset=5, y_offset=40.5, render_mode='canvas')

        stdev_label.text_font_size = "12pt"

        p.add_layout(stdev_label)

    mean_heading = Label(x=1400, y=10, text='Mean', text_font_style='bold',
                       x_offset=25, y_offset=66, render_mode='canvas', angle=90, angle_units="deg")
    mean_heading.text_font_size = "12pt"

 

    p.add_layout(mean_heading)

    stdev_heading = Label(x=1500, y=10, text='StDev', text_font_style='bold',
                         x_offset=25, y_offset=66, render_mode='canvas',angle=90, angle_units="deg")

    stdev_heading.text_font_size = "12pt"

    p.add_layout(stdev_heading)
    
    
    
    p.yaxis.bounds = (0.4999, 12)
    my_title = Title(text=title_text, text_font=font,
                     text_font_size="21pt",
                     align='center', text_line_height=1, vertical_align='middle', standoff=50)
    
    p.add_layout(my_title, 'above')
    
    show(p)
    
    return p


if __name__ == '__main__':
    
    # set up date_range and benchmark_list
    
    date_range, benchmark_list = setup_date_range_and_benchmark_list()
    
    p1=draw_ridge_graph(benchmark_list, date_range, actual_funds=True)

    export_png(p1, filename="show_active_share_actual_positions_distributions_plot.png")

    p2=draw_ridge_graph(benchmark_list, date_range, actual_funds=False)

    export_png(p2, filename="show_active_share_implied_positions_distributions_plot.png")
    
    