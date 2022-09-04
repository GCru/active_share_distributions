from bokeh.plotting import figure, output_file, show
from bokeh.models import Label, LinearAxis, Title
from bokeh.models.tickers import FixedTicker
from bokeh.models import Arrow, NormalHead, OpenHead, VeeHead, LabelSet
from bokeh.models import Range1d
from bokeh.models import ColumnDataSource

from bokeh.io import export_png
from bokeh.util.compiler import TypeScript

import math

from latex_label_utility import LatexLabel

from bokeh_constants import *


# output to static HTML file


def distance_plot():
	# Plot one which shows the distance measure
	output_file("line.html")
	
	p = figure(plot_width=int(500), plot_height=500)
	
	my_title = Title(text="Measuring portfolio distances", text_font=font,
					 align='center', text_font_size=double_graph_title_font_size, text_line_height=1, vertical_align='middle')
	
	p.add_layout(my_title, 'above')
	
	p.toolbar.logo = None
	p.toolbar_location = None
	
	p.line([-0.1, 1.1], [1.1, -0.1], line_width=3, color="black")
	
	#p.step([0.2, 0.8], [0.8, 0.2], line_width=2, color="grey")
	
	arrow_up_d1 = Arrow(end=NormalHead(fill_color="grey", size=10), x_start=0.2, y_start=0.2 ,
					 x_end=0.20, y_end=0.78)
	
	p.add_layout(arrow_up_d1)
	
	arrow_across_d1 = Arrow(end=NormalHead(fill_color="grey", size=10), x_start=0.2, y_start=0.2,
						x_end=0.77, y_end=0.2)
	
	p.add_layout(arrow_across_d1)
	
	
	# set up Y-axis
	
	p.yaxis.fixed_location = 0
	p.yaxis.ticker = FixedTicker(ticks=[0.2 + i * 0.2 for i in range(0, 5)])
	
	# set up x_axis
	
	p.xaxis.fixed_location = 0
	p.xaxis.axis_label = 'Share 1'
	# p.xaxis.axis_label_visible = True
	p.xaxis.axis_label_standoff = 0
	p.xaxis.visible = True
	
	p.axis.axis_label_text_font_size = double_graph_axis_label_font_size
	p.xaxis.axis_label_text_font = font
	p.yaxis.axis_label_text_font = font
	
	p.axis.major_label_text_font_size = double_graph_major_label_font_size
	p.xaxis.major_label_text_font = font
	p.yaxis.major_label_text_font = font
	
	p.xaxis.ticker = FixedTicker(ticks=[0.2 + i * 0.2 for i in range(0, 5)])
	
	# plot.xaxis.ticker = x_values
	# plot.xaxis.major_label_overrides = override_dict
	# plot.xaxis.major_label_orientation = pi / 4
	
	# add a circle renderer with a size, color, and alpha
	p.circle([0.2, 0.8], [0.8, 0.2], size=17.5, line_color="grey", line_width=3, alpha=0.8, fill_color=None)
	p.grid.bounds = (0.2, 1.1)
	
	portfolio_label = Label(x=0.25, y=0.85, text='P = Portfolio', text_font=font,
							border_line_color=None,
							background_fill_color='white', background_fill_alpha=1.0)
	
	index_label = Label(x=0.85, y=0.23, text='B = Benchmark', text_font=font,
						border_line_color=None,
						background_fill_color='white', background_fill_alpha=1.0)
	
	# label_l_1 = Label(x=0.45, y=0.11, text='l\u2081',
	#				  border_line_color=None,
	#				  background_fill_color='white', background_fill_alpha=1.0)
	# p.add_layout(label_l_1)
	
	# label_l_2 = Label(x=0.15, y=0.45, text='l\u2082',
	#				  border_line_color=None,
	#				  background_fill_color='white', background_fill_alpha=1.0)
	# p.add_layout(label_l_2)
	
	#label_d_2 = Label(x=0.5, y=0.52, text='D\u2082', text_font=font,
	#				  border_line_color=None,
	#				  background_fill_color='white', background_fill_alpha=1.0)
	
	#label_d_2 = LatexLabel(x=0.5, y=0.57, text="A_{\\mathrm{Euclid}} = \\mathrm{Euclidean \; Active \; Share}",
	#					   text_font=font,
	#					   render_mode="css", text_font_size="12px", background_fill_alpha=0)
	#p.add_layout(label_d_2)
	
	label_d_2 = LatexLabel(x=0.5, y=0.50, text="A_{\\mathrm{Euclid}} = \\mathrm{Euclidean \; Active \; Share}", text_font=font,
					  render_mode="css", text_font_size="12px", background_fill_alpha=0)
	p.add_layout(label_d_2)
	
	latex_label_w_1 = LatexLabel(
		text="w_{P\\text{-}B,1}",
		x=0.38,
		y=0.11,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size="12px",
		background_fill_alpha=0)
	
	p.add_layout(latex_label_w_1)
	
	latex_label_w_2 = LatexLabel(
		text="w_{P\\text{-}B,2}",
		x=0.07,
		y=0.48,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size="12px",
		background_fill_alpha=0)
	
	p.add_layout(latex_label_w_2)
	
	latex_label_B_conc = LatexLabel(
		text="B_{\\mathrm{conc}} = \mathrm{Concentration\; Index}",
		x=0.350,
		y=0.03,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size="12px",
		background_fill_alpha=0)
	
	p.add_layout(latex_label_B_conc)
	
	latex_label_d_1 = LatexLabel(
		text="2A_{\\mathrm{Mhtn}} = ",
		x=0.18,
		y=0.45,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size="12px",
		background_fill_alpha=0, angle =270, angle_units="deg")
	
	p.add_layout(latex_label_d_1)
	
	latex_label_d_1_more = LatexLabel(
		text=" 2 \\, \mathrm{Manhattan\; Active \; Share}",
		x=0.23,
		y=0.17,
		# x_units="screen",
		# y_units="screen",
		render_mode="css",
		text_font_size="12px",
		background_fill_alpha=0)
	
	p.add_layout(latex_label_d_1_more)
	
	y_margin = 0.07
	arrow_up = Arrow(end=NormalHead(fill_color="black", size=10), x_start=0.475, y_start=0.525 + y_margin,
					 x_end=0.2 + 0.03, y_end=0.8 + y_margin - 0.03)
	p.add_layout(arrow_up)
	
	arrow_down = Arrow(end=NormalHead(fill_color="black", size=10), x_start=0.56, y_start=0.44 + y_margin,
					   x_end=0.8 + 0.03, y_end=0.2 + y_margin - 0.03)
	p.add_layout(arrow_down)
	
	arrow_up_conc = Arrow(end=NormalHead(fill_color="black", size=10), x_start=0.420, y_start=(0.420 * 0.2 / 0.8),
						  x_end=0.8, y_end=(0.8 * 0.2 / 0.8), line_dash="dashed")
						  
	#					  x_end=0.8, y_end=0.2, line_dash="dashed")
	p.add_layout(arrow_up_conc)
	
	arrow_down_conc = Arrow(end=NormalHead(fill_color="black", size=10), x_start=0.325, y_start=(0.325 * 0.2 / 0.8),
							x_end=0.0, y_end=0.0, line_dash="dashed")
	p.add_layout(arrow_down_conc)
	
	p.add_layout(portfolio_label)
	p.add_layout(index_label)
	
	extra_y_axis = LinearAxis(
		axis_label="Share 2", axis_label_text_color="black", axis_label_text_font_style="bold", axis_line_alpha=0,
		axis_label_standoff=0, axis_label_text_font_size=graph_axis_label_font_size,
		major_tick_line_alpha=0, minor_tick_line_alpha=0, major_label_text_alpha=0)
	p.add_layout(extra_y_axis, 'left')
	
	extra_x_axis = LinearAxis(axis_label="Share 1", axis_label_text_color="black", axis_label_text_font_style="bold",
							  axis_line_alpha=0,axis_label_text_font_size=graph_axis_label_font_size,
							  axis_label_standoff=0,
							  major_tick_line_alpha=0, minor_tick_line_alpha=0, major_label_text_alpha=0)
	p.add_layout(extra_x_axis, 'below')
	
	# show the results
	show(p)
	export_png(p, filename="explaining_active_share_plot.png")
	
	return




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
	distance_plot()

