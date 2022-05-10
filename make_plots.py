#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import argparse

def get_args():

    parser = argparse.ArgumentParser(
        description = 'Input synced file, output plots',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-file',
                        metavar='FILE',
                        type=argparse.FileType('rt'),
                        help='synced data file path, in quotations',
                        default='synced_data.csv')
    
    parser.add_argument('-c1',
                        metavar='str1',
                        help = 'Flopatch column to be plotted, in quotations',
                        default='Vmax VTI Total')
    
    parser.add_argument('-c2',
                        metavar='str2',
                        help='Nexfin column to be plotted, in quotations',
                        default='CO')
    
    return parser.parse_args()

def main():
    args = get_args()
    make_plots(args.file, args.c1, args.c2)


# function for making plot
def make_plots(data, variable1, variable2):

    data = pd.read_csv(data)

    # where variable 1 is a flopatch column, and variable 2 is a nexfin column

    data = data.dropna(subset = variable1)

    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('flopatch: ' + variable1, color = color)
    ax1.plot(data['TimeSec'], data[variable1], color = color, alpha = 1)
    ax1.tick_params(axis = 'y', labelcolor = color)

    ax2 = ax1.twinx()

    color = 'tab:grey'
    ax2.set_ylabel('nexfin: ' + variable2, color = color)
    ax2.plot(data['TimeSec'], data[variable2], color = color, alpha = 0.8)
    ax2.tick_params(axis = 'y', labelcolor = color)

    fig.suptitle('Flopatch: ' + variable1 + ' vs. Nexfin: ' + variable2, fontweight = 'bold')

    plt.savefig(variable1 + variable2 + '.jpg')
    
if __name__ == '__main__':
    main()
    print("Done")