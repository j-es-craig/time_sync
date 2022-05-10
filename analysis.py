#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
import argparse

# goal is to find the correlation between the two variables, using either the pearson / spearman correlation coeff
# then, find the cross correlation coefficiecnt (ccf)
# I want to output 1) summary stats, 2) general linear regression, 3) ccf to describe the relatinship between Vmax VTI and CO

def get_args():

    parser = argparse.ArgumentParser(
        description = 'Input synced file, output stats and plot of linear regression',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-file',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        help='synced file, in quotations',
                        default='synced_data.csv')
    
    parser.add_argument('-c1',
                        metavar='str1',
                        help = 'Flopatch column to be plotted, in quotations',
                        default = 'Vmax VTI Total')
    
    parser.add_argument('-c2',
                        metavar='str2',
                        help='Nexfin column to be plotted, in quotations',
                        default='CO')

    return parser.parse_args()

def main():
    args = get_args()

    print(find_relationship(args.file, args.c1, args.c2))

def find_relationship(data, variable1, variable2):

    # data = synced data file
    # variable1 = flopatch column
    # variable2 = nexfin column

    data = pd.read_csv(data)
    data = data.dropna(subset=variable1)
    data = data[[variable1, variable2]]

    # remove outliers
    Q1 = data.quantile(q=.25)
    Q3 = data.quantile(q = .75)
    IQR = data.apply(stats.iqr)
    data_clean = data[~((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).any(axis=1)]

    # calculate summary stats
    descriptive_stats = data_clean.describe()
    print("Summary Statistics: ")
    print(descriptive_stats)

    # do linear regression
    y = data_clean[variable2]
    x = data_clean[variable1]
    x = sm.add_constant(data_clean[variable1])
    model = sm.OLS(y, x).fit()
    preds = model.predict()
    print(model.summary())

    # plot variables
    plt.scatter(data_clean[variable1], data_clean[variable2])
    yhat = model.params[1].astype(int) * data_clean[variable1] + model.params[0].astype(int)
    plt.plot(data_clean[variable1], preds, lw = 3, c = 'red', label = 'regression line')
    plt.title('Flopatch: ' + variable1 + ' vs. Nexfin: ' + variable2, fontweight = 'bold')
    plt.xlabel(variable1)
    plt.ylabel(variable2)
    plt.savefig(variable1 + variable2 + 'regression.jpg')

    # make qq plot
    res = model.resid
    fig = sm.qqplot(res, fit = True, line = '45')
    plt.savefig(variable1 + variable2 + 'qqplot.jpg')

if __name__ == '__main__':
    main()