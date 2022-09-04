from scipy.stats import chi, kstest, ks_2samp, norm, lognorm
from scipy.special import psi, gamma
from scipy.optimize import fsolve, minimize

import numpy


from bokeh.plotting import figure, output_file, show
from bokeh.models import Range1d, PrintfTickFormatter, NumeralTickFormatter, Title, DatetimeTickFormatter
from bokeh.layouts import row
from bokeh.io import output_file, show
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
from bokeh.models.tickers import FixedTicker
from bokeh.io import export_png

from bokeh_constants import *

from shared_with_active_risk_paper import make_histogram


def draw_active_share_histogram(data_list, data_list_2, k, sigma, bins="auto", density_histogram=False):
   
    # create histogram data
    frequency_list, bin_edges_list = make_histogram(data_list, bins=bins, density_histogram=density_histogram)
    left_edges = bin_edges_list[:-1]
    right_edges = bin_edges_list[1:]
    
    if data_list_2 is not None:
        frequency_list_2 = [0 for _ in frequency_list]
        for i in range(len(left_edges)-1):
            for item in data_list_2:
                if item > left_edges[i] and item <= left_edges[i+1]:
                    frequency_list_2[i] = frequency_list_2[i] + 1
        frequency_list_2 = [frequency_list_2[i]/len(data_list_2) for i in range(len(frequency_list))]
    
        data = {'frequency': frequency_list, 'frequency_2': frequency_list_2,'left_edges': left_edges, 'right_edges': right_edges}
        
    else:
        data = {'frequency': frequency_list, 'left_edges': left_edges,
                'right_edges': right_edges}
    source = ColumnDataSource(data=data)
    
    # Set up plot
    plot = figure(plot_width=int(500), plot_height=500)
    #plot.toolbar.logo = None
    #plot.toolbar_location = None
    
    """my_title = Title(text=my_title, align='center',
                     text_font=font, text_font_size=double_graph_title_font_size,
                     text_line_height=1, vertical_align='middle')
    plot.add_layout(my_title, "above")
    
    
    min_x = 0
    max_x = 5
    max_y = 0.35
    plot.xaxis.axis_label = 'Standard deviation of standard score distributions'
    plot.xaxis.ticker = FixedTicker(ticks=[3, 5, 10, 15, 20, 25, 30, 35])
    
    plot.x_range = Range1d(min_x, max_x)  # left_edges[0], right_edges[-1])
    
    # plot.xaxis[0].formatter = PrintfTickFormatter(format="%2.0f%%")
    plot.min_border_right = 20
    plot.min_border_bottom = 30
    
    plot.yaxis.axis_label = 'Relative frequency'
    plot.yaxis[0].formatter = NumeralTickFormatter(format="0.1%")
    plot.y_range = Range1d(0.0, max_y)
    
    plot.axis.axis_label_text_font_size = double_graph_axis_label_font_size
    plot.xaxis.axis_label_text_font = font
    plot.yaxis.axis_label_text_font = font
    
    plot.axis.major_label_text_font_size = double_graph_major_label_font_size
    plot.xaxis.major_label_text_font = font
    plot.yaxis.major_label_text_font = font"""
    
    # construct histogram
    r0 = plot.quad(
        bottom=0, top='frequency', left='left_edges', right='right_edges', source=source,
        fill_color='lightgrey', line_color='black')  # legend='Underperforming monkey portfolios')
   

    #r1 = plot.quad(
    #    bottom=0, top='frequency_2', left='left_edges', right='right_edges', source=source,
    #    fill_color='none', line_color='black')  # legend='Underperforming monkey portfolios')
    
    if data_list_2 is not None:
        plot.line(left_edges, frequency_list_2)


    #df = 2
    #x = numpy.linspace(chi.ppf(0.0000001, df), chi.ppf(0.99999999, df), 100)
    x = numpy.linspace(0,right_edges[-1], 10000)
    
    #pdf = chi.pdf(x,df, scale = 1)
    #plot.line(x, pdf, line_color='black', line_width=4, alpha=0.7, legend_label="Chi distribution")

    df = k   #(df*40)**(0.5)
    if density_histogram == True:
        pdf_chi = chi.pdf(x, df, loc=0, scale=sigma)
        
    else:
        pdf_chi = chi.pdf(x, df, loc=0, scale=sigma) *(right_edges[2]-right_edges[1])
        
        loc1, scale1 = norm.fit(data_list)
        print()
        pdf_normal = norm.pdf(x, loc=loc1, scale=scale1)*(right_edges[2]-right_edges[1])
        #pdf_lognormal = lognorm.pdf(x,s=1.3        , loc=0.0, scale=0.1)*(right_edges[2]-right_edges[1])
        
    #x = numpy.linspace(chi.ppf(0.0000001, df), chi.ppf(0.99999999, df), 100)

    plot.line(x, pdf_chi, line_color='blue', line_width=4, alpha=0.7, legend_label="Chi distribution")

    plot.line(x, pdf_normal, line_color='green', line_width=4, alpha=0.7, legend_label="Normal distribution")

    #plot.line(x, pdf_lognormal, line_color='red', line_width=4, alpha=0.7, legend_label="Chi distribution")
    
    
    return plot


def chi_scaled_pdf(x, k, sigma):
    """ Calculate chi pdf
    :param x: At which point to calculate the probability
    :param k: Degrees
    :param sigma: Scaling
    :return:
    """
    # https: // math.stackexchange.com / questions / 1009938 / probability - density - function - of - scaled - gamma - random - variable
    
    # My own formula
    f_factor = 1 / (2 ** ((k / 2) - 1) * gamma(k / 2))
    f_factor = f_factor * (x / sigma) ** (k - 1)
    f_factor = f_factor * numpy.exp(-x * x / (2 * sigma * sigma))
    
    # Equivalent scipy formula
    # chi.pdf(x, k, scale=sigma) * sigma
    
    return f_factor/sigma


def L_max_chi(k, sigma, data):
    """  Calculate with log on outside
    :param k:
    :param sigma:
    :param data:
    :return:
    """
    f = 0
    for i in range(0, data.size):
        f_factor = 1 / (2 ** ((k / 2) - 1) * gamma(k / 2))
        f_factor = f_factor * (data[i] ** (k - 1) / sigma ** k)
        f_factor = f_factor * numpy.exp(-data[i] * data[i] / (2 * sigma * sigma))
        
        f = f + numpy.log(f_factor)
    
    return f


def l_max_chi(k, sigma, data):
    """ Calculate with log likelihood on inside
    :param k:
    :param sigma:
    :param data:
    :return:
    """
    
    N = data.size
    
    f = -N * (k / 2 - 1) * numpy.log(2) - N * numpy.log(gamma(k / 2))
    
    f = f - N * k * numpy.log(sigma) + (k - 1) * numpy.sum(numpy.log(data)) - numpy.dot(data, data) / (
                2 * sigma * sigma)
    
    return f


def generate_random_chi_scaled(k, sigma, N):
    """My version of generating random chi values.
    :param k:
    :param sigma:
    :param N:
    :return:
    """
    
    # https://stackoverflow.com/questions/4265988/generate-random-numbers-with-a-given-numerical-distribution
    
    step =0.001
    a = numpy.arange(0,2000,0.001, dtype=float)

    f = lambda x: chi_scaled_pdf(x,k,sigma)*step

    p= f(a)
    data = numpy.random.choice(a, p=p, size = N)
    
    return data


def generate_random_chi(k, sigma, N):
    """ Scipy generate random chi values
    :param k:
    :param sigma:
    :param N:
    :return:
    """
    
    df = k
    data = chi.rvs(df, size=N,scale = sigma )

    return data


class ChiMaxLikelihood(object):
    
    def __init__(self, data):
        
        self.data = data
        self.N = len(data)

    def func_for_k(self, k):
        # https://stats.stackexchange.com/questions/267854/estimating-the-number-of-degrees-of-freedom-in-a-chi-squared-distribution
    
        sigma = ( numpy.dot(self.data,self.data)/(self.N*k) ) **0.5
    
        f = -0.5*self.N*numpy.log(2) - 0.5*self.N *psi (k/2)
        f= f- self.N* numpy.log(sigma)  #
        f= f+numpy.sum(numpy.log(self.data))
        
        #print('sigma within' , ( numpy.dot(self.data,self.data)/(self.N*(k-1)) ) **0.5)
    
        return f
    
    def solve_k_sigma(self, k_guess=10):
        
        k = fsolve(self.func_for_k, [k_guess,])
        sigma = numpy.dot(self.data,self.data)/(self.N*k)
        
        return k, sigma**0.5


class ChiKSTest(object):
    
    def __init__(self, data):
        self.data = data
        self.N = len(data)
    
    def func_for_k_sigma(self, x0):
        # https://stats.stackexchange.com/questions/267854/estimating-the-number-of-degrees-of-freedom-in-a-chi-squared-distribution
        if x0[0] <= 0 or x0[1] <= 0:
            return 100
        k=x0[0]
        sigma=x0[1]
        print('x0', x0)
        x = numpy.linspace(0, 10, 10000)
        ks_statistic, p_value = ks_2samp(self.data,  chi.rvs(df=k, size=self.N,scale = sigma ))
        #chi.pdf(x, df=k, loc=0, scale=sigma) )
        print('KS stats',ks_statistic, p_value)
        
        return ks_statistic
    
    def solve_k_sigma(self, k_guess=5, sigma_guess=0.05):
        
        res = minimize(self.func_for_k_sigma, [k_guess,sigma_guess ], method='Powell')
        
        return res.x[0], res.x[1]


def dl_dk_chi(k, sigma, data):
    
    N= data.size
    f = -(N  / 2) * numpy.log(2) - (N/2) * psi(k/2) - N * numpy.log(sigma) +  numpy.sum(numpy.log(data))
    
    return f

def dl_dsigma_chi(k, sigma, data):
    
    N = data.size
    f = (-N*k/sigma) +numpy.dot(data,data)/(sigma*sigma*sigma)
    
    return f
    



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   
    N=10000
    k=50 #8
    sigma=1/50
    
    print('Active share:', (sigma**2*k)**0.5)
    print('Stdev position size as proportion of total portfolio:', sigma)
   
    
    # Check whether my chi and scipy chi are the same
    #print( chi.pdf(0.2, k, scale=sigma),chi_scaled_pdf(0.2,k,sigma))
    
    # Genrate random data for test
    data = generate_random_chi(k, sigma,N)
    print(dl_dsigma_chi(10, 10, data))
    print('Check L and l', l_max_chi(k, sigma-1, data), l_max_chi(k, sigma-1, data))
    # Plot histogram of random data along with chi to see if it works
    plot_density = draw_active_share_histogram(data, k=k, sigma=sigma, density_histogram=False)
    show(plot_density)
    
    exit()
    
    # find k and sigma that gives maximum
    """biggest = -1000000000
    for i in range(90, 110):
        for j in range(80, 110):
            
            test_k=i/10
            test_sigma = j/10
            l_l = l_max(test_k,test_sigma ,data)
            if l_l > biggest:
                biggest = l_l
                keep_k = test_k
                keep_sigma = test_sigma
               

    print(keep_k, keep_sigma)"""
    
    chi_ks_test =ChiKSTest(data)
    k=k-5
    sigm=sigma+10
    k_solved, sigma_solved = chi_ks_test.solve_k_sigma(k,sigma)
    
    print('KS test', k_solved, sigma_solved)
    exit()

    chi_max_likelihood = ChiMaxLikelihood(data)

    k_solved, sigma_solved = chi_max_likelihood.solve_k_sigma()
    
    print('solved', k_solved,sigma_solved)
    
   
    plot_frequency = draw_active_share_histogram(data, k=k, sigma=sigma, density_histogram=False)
    show(row(plot_frequency, plot_density))

    k=10
    sigma =1
    x = numpy.linspace(0, 20, 10000)
    pdf = chi.pdf(x, k, loc=0, scale=sigma)
    print(chi.stats(k,moments='mvsk'))
    
    k=10
    sigma =2
    x = numpy.linspace(0, 20, 10000)
    pdf = chi.pdf(x, k, loc=0, scale=sigma)
    print(chi.stats(k,scale=sigma,moments='mvsk'))
    
    print(sigma*sigma*chi.stats(k,moments='v'))