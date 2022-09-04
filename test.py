from bokeh.plotting import figure, show

categories = ['A', 'B','C' ]

p = figure(y_range=categories)
p.circle(y=categories, x=[4, 6, 5], size=20)

p.xaxis.fixed_location = 0.5
p.xaxis.bounds =(4,7)

p.yaxis.fixed_location= 4
p.yaxis.bounds = (0.499,3)

show(p)