import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path
from download import *
import argparse




def plot_stat(data_source, fig_location = None, show_figure = False, years = ['2016', '2017', '2018', '2019','2020']):
    """vytvori graf pro tuple(list[str], list[np.ndarray]) rozdelen na jednotlive podgrafy podle let a sloupce podle regionu"""
    list_of_data_per_year = list()
    regions = list(set(data_source[1][0])) #ziskani vsech kraju ktere jsou v data_source
    for year in years:
        my_dict = dict.fromkeys(regions, 0)
        for i in range(len(data_source[1][0])):
            if data_source[1][4][i].astype(object).year == int(year):
                for region in regions:
                    if  data_source[1][0][i] == region:
                        my_dict[region] += 1
        list_of_data_per_year.append(my_dict)
    
    fig, axs = plt.subplots(len(years), 1)
    fig.set_size_inches(11.5, 18.5)
    fig.tight_layout(rect=[0, 0.03, 1, 0.95], pad=3.0)
    fig.set_facecolor(color='#3E3E3F')
    fig.suptitle('Pocet nehod v jednotlivych krajich', color='#BE8A16', size=40, weight=100)
    #adding subplots
    for ax, data, year in zip(axs, list_of_data_per_year, years):
        ax.bar(list(data.keys()),list(data.values()),color='#BE8A16')
        #show value over bars
        sorted_values = sorted(list(data.values()), reverse=True)
        for x, v in enumerate(list(data.values())):
            ax.text(x-0.3,800, str(sorted_values.index(v) + 1) + '.', weight=800, size=9)
            ax.text(x,800, str(v), weight=800, size=9)

        ax.set_title(year, color='#BE8A16', size=20, weight=100)
        ax.set_facecolor(color='#202020')
        ax.yaxis.set_visible(False)
        ax.xaxis.set_tick_params(which='major',labelcolor='#BE8A16', labelsize='large')
    
    if show_figure:
        plt.show()
    if fig_location != None:
        Path(fig_location).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(fig_location)
    plt.close(fig)

if __name__ == "__main__":
    downloader = DataDownloader()
    data = downloader.get_list(regions=['PHA', 'STC', 'JHC'])

    parser = argparse.ArgumentParser(description='args for plot_stat')
    parser.add_argument("--fig_location", action="store", dest="fig_location", default=None)
    parser.add_argument("--show_figure", action="store", dest="show_figure", default=False)
    arguments = parser.parse_args()
    if arguments.show_figure:
        print('Graf v souboru vypada lepe')
    plot_stat(data, fig_location = arguments.fig_location, show_figure = arguments.show_figure)
