import pandas as pd                        
from pytrends.request import TrendReq
pytrend = TrendReq()

import matplotlib.pyplot as plt
import os

project_dir = os.getcwd()

def trend_visualization(word, year_s, year_f):

    kw_list = [word]

    historical_trends = pytrend.get_historical_interest(kw_list, year_start=year_s, month_start=1, day_start=1, hour_start=0, 
                                 year_end=year_f, month_end=12, day_end=31, hour_end=0, cat=0, geo='', gprop='', sleep=0)

    list_of_datetimes = list(historical_trends.index)
    values = historical_trends[kw_list[0]]
    plt.plot(list_of_datetimes, values)

    plt.gcf().autofmt_xdate()
    plt.grid(True)
    plt.ylabel('World frequency of word ' + kw_list[0].upper() +' requests')
    plt.savefig(project_dir + r'\static\images\new_plot.png', dpi = 1000)
    plt.show()
