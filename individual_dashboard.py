"""
# Make Individual Dashboards

This script makes dashboard graphs

* Depends on ./FCN.csv
* Depends on ./providers/ with individual csv files named like First_Last.csv
* csv files are created from Meridios History on Core Quality Report. 
* Creates graphs in ./output/
"""

"""
## Import modules needed. 

* **Numpy:** Numerical Analysis needed for Pandas
* **Pandas:** Data wrangling (dataframes, pivots, grouping.)
* **Matplotlib:** 2D Graphing library
* **Seaborn:** Further add ons to Matplotlib for more complicated graphs.
* **glob:** Filename function to get CSVs 
* **datetime:** Used to clean time stamps (to round times to midnight.)
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob as glob
import datetime

# Use Matplotlib's 538 format
plt.style.use('fivethirtyeight') 
# but override the default font.
plt.rcParams["font.family"] = "Adobe Gothic Std" 

"""
## Read CSV file and returns a dataframe

* Uses Provider Name (Could be individual or clinic)
* Full CSV location (could be ./provider/ or ./clinic/
* Adds the provider name as an additional column of data
"""
def get_meridios_quality_history_csv(provider, csv):
    df = pd.read_csv(csv, 
                     usecols=["lastupdate", "metricname", "ptsseen_avg"], 
                     parse_dates=["lastupdate"])
    # Add a column to the dataframe with provider name
    df['Provider'] = provider.replace("_", " ")
    # Normalize last update to just a date (not specific run time)
    df['lastupdate'] = df['lastupdate'].apply(lambda dt: datetime.datetime(dt.year, dt.month, dt.day))
    return df

"""
## Creates a basic trendline chart

Arguments:

* dataframe: the data to graph
* chart: the ax to use in a subplots
* column: the data to graph
* metrictitle: The 'pretty name' to use on the chart
* threshold: Number (0-100) to be used for the green target line.
"""
def basic_trendline(dataframe, chart, column, metrictitle, threshold):
    dataframe[column].plot(ax=chart, legend=False)
    chart.set(title=metrictitle, ylim=(0,100), xlabel="")
    # Threshold line is green from 538 palette: 6d904f
    chart.axhline(y=threshold, color='#6d904f', label='NCQA 90%ile', linestyle='--', linewidth=2, zorder=5)  
    # Don't show x axis -- too noisy with 9 plots.  
    chart.xaxis.set_major_formatter(plt.NullFormatter())
    
"""
## Creates a dashboard of core measures

Arguments:

* individual: Provider Name as First_Last
"""
def create_individual_core_quality_graphs(individual):
    dfs = []
    # Location of FCN.csv is hardcoded. 
    dfs.append(get_meridios_quality_history_csv('FCN',"FCN.csv"))
    dfs.append(get_meridios_quality_history_csv(individual, ('./provider/' + individual + '.csv')))
    big_frame = pd.concat(dfs, ignore_index=True)
    big_frame = big_frame.pivot_table(index='lastupdate', columns=['metricname','Provider'], values="ptsseen_avg")
    
    # Summary Graph is 3 by 3 Chart with shared y axes. 
    fig, ax = plt.subplots(nrows=3, ncols=3, sharey=True, figsize=(9,9))
    # Add some whitespace to graphs
    fig.subplots_adjust(wspace = 0.5, hspace = 0.5) 
    fig.suptitle(individual.replace("_", " ") + ": Core Quality Measures", fontsize=24)
    
    basic_trendline(big_frame, ax[0][0], "PAP", "Pap", 85)
    basic_trendline(big_frame, ax[0][1], "MAMMO", "Mammogram", 78)
    basic_trendline(big_frame, ax[0][2], "COLORECTAL", "Colorectal", 76)
    
    basic_trendline(big_frame, ax[1][0], "DM-EYE", "Retinopathy (DM)", 76)
    basic_trendline(big_frame, ax[1][1], "DM-FOOT", "Neuropathy (DM)", 77)
    basic_trendline(big_frame, ax[1][2], "DM-KIDNEY", "Nephropathy (DM)", 80)

    basic_trendline(big_frame, ax[2][0], "TDAP", "Tdap", 80)
    basic_trendline(big_frame, ax[2][1], "DM-PPSV", "Pneumovax (DM)", 80)
    # We don't need the 9th chart.
    fig.delaxes(ax[2][2])
# * '008fd5' blue
# * 'fc4f30' red
# * 'e5ae38' yellowish
# * '6d904f' green
# * '8b8b8b' gray
# * '810f7c' purple
# 
# We're manually setting the provider color as purple, FCN as blue. (Could've done a manual sort.)   
    if (individual > "FCN"):
        for ax in fig.axes:
            ax.get_lines()[0].set_color("#008fd5")
            ax.get_lines()[1].set_color("#810f7c")
    else:
        for ax in fig.axes:
            ax.get_lines()[0].set_color("#810f7c")
            ax.get_lines()[1].set_color("#008fd5")

# Legend Text is hardcoded here. 
    plt.figtext(0.70,0.37,'1/1 through 10/31/2017',fontsize=14,ha='left')
# Manual Colors in Legend
    plt.figtext(0.70,0.34,'FCN',fontsize=14,ha='left',color="#008fd5")
    plt.figtext(0.70,0.31,individual.replace("_", " "),fontsize=14,ha='left',color="#810f7c")
    plt.figtext(0.70,0.28,'Target',fontsize=14,ha='left',color="#6d904f")
# Save the files in the ./output/ folder. 
    plt.savefig("./output/" + individual + ".png")

# ## Get the filenames for each of the provider CSVs
files = glob.glob('./provider/*.csv')

# ## Create one graph for each provider.
for file in files:
    individual = file.replace('./provider/',"")
    individual = individual[:-4]
    create_individual_core_quality_graphs(individual)