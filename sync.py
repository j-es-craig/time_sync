#!/usr/bin/env python3

import pandas as pd
import argparse
import time

def get_args():

    parser = argparse.ArgumentParser(
        description = 'Input two unsynced files, output one synced file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('-file1',
                        metavar='FILE1',
                        type=argparse.FileType('rt'),
                        help='flopatch filepath, in quotations',
                        default = 'fpdata_reformat.csv')

    parser.add_argument('-file2',
                        metavar='FILE2',
                        type=argparse.FileType('rt'),
                        help='nexfin filepath, in quotations',
                        default = 'labchartdata.csv')
    
    parser.add_argument('-ns',
                        metavar='int',
                        type=int,
                        help='Number of stages in flopatch data',
                        default = 3)

    parser.add_argument('-scale',
                        metavar = 'int',
                        type = int,
                        help = 'run either scalable version (0) or manual version (1). Manual might be slighlty faster',
                        default = '0')
    
    return parser.parse_args()

def main():
    args = get_args()

    start = time.time()
    print("Synchronization Start")
    
    # read in data
    flowpatch = pd.read_csv(args.file1)
    nexfin = pd.read_csv(args.file2)

    # rename flowpatch time column and stage
    flowpatch.rename(columns={'Time (s)': 'TimeSec'}, inplace = True)
    flowpatch.loc[flowpatch['Stage']=='B', 'Stage'] = '0'
    flowpatch['TimeSec'] = flowpatch['TimeSec'].round(decimals = 3)

    # adjust time column for flowpatch, the break up into smaller dfs
    flowpatch['TimeSec'] = flowpatch.apply(lambda row: row['TimeSec'] + int(row['Stage']) * 300, axis=1) 
    
    if args.scale == 0:

        splits = list(flowpatch.groupby('Stage'))

        # take only nexfin data we have flopatch stages for
        nexfin_cropped = nexfin[nexfin['TimeSec'] < args.ns * 300]   

        # run function to determine how much i need to adjust flopatch by
        for i in range(len(splits[0]) + 1):
            print("Working on stage: " + str(i))
            adjust = sum_of_diffs(splits[i][1], nexfin_cropped, i + 1)
            splits[i][1]['TimeSec'] = splits[i][1]['TimeSec'] + adjust
            print("Done stage: " + str(i))
            
        recombined = pd.concat([splits[0][1], splits[1][1], splits[2][1]], sort = False)

        complete = pd.merge(left = recombined, right = nexfin_cropped, on = 'TimeSec', how = 'right')

        complete.to_csv('synced_data.csv')

        end = time.time()
        print(end - start)
        print("Done")

    elif args.scale == 1:
        print("Step 1 Done")
        stage_B = flowpatch[flowpatch['Stage'] == '0']
        stage_1 = flowpatch[flowpatch['Stage'] == '1']
        stage_2 = flowpatch[flowpatch['Stage'] == '2']

        nexfin_stage_B = nexfin[nexfin['TimeSec'] < 300]
        nexfin_stage_1 = nexfin[(nexfin['TimeSec'] >= 300) & (nexfin['TimeSec'] < 600)]
        nexfin_stage_2 = nexfin[(nexfin['TimeSec'] >= 600) & (nexfin['TimeSec'] < 900)]

        test_obj_b_list = sum_of_diffs(stage_B, nexfin_stage_B, 1)
        print("Stage 0 Done")
        test_obj_1_list = sum_of_diffs(stage_1, nexfin_stage_1, 2)
        print("Stage 1 Done")
        test_obj_2_list = sum_of_diffs(stage_2, nexfin_stage_2, 3)
        print("Stage 2 Done")

        stage_B['TimeSec'] = stage_B['TimeSec'] + test_obj_b_list
        stage_1['TimeSec'] = stage_1['TimeSec'] + test_obj_1_list
        stage_2['TimeSec'] = stage_2['TimeSec'] + test_obj_2_list

        stage_B_combined = pd.merge(left = stage_B, right = nexfin_stage_B, on = 'TimeSec', how = 'right')
        stage_1_combined = pd.merge(left = stage_1, right = nexfin_stage_1, on = 'TimeSec', how = 'right')
        stage_2_combined = pd.merge(left = stage_2, right = nexfin_stage_2, on = 'TimeSec', how = 'right')

        recombined = pd.concat([stage_B_combined, stage_1_combined, stage_2_combined], sort = False)

        recombined.to_csv('synced_data_manual.csv')

        end = time.time()
        print(end - start)
        print("Done")
    
    else:
        print("error")

        end = time.time()
        print(end - start)
        print("Done")


# this function will find the best time alignment for the datasets based on HR
# finds the alignment that produces the smallest differences in HR, we use that to then adjust the original dataframes
# this can be optimized by using heuristics to cut out unnecessary checks, by using asyncronous processing with asyncio, or multiprocessing
# i understand it might be better to try and line them up using PSV and ECG, and while I did find some research on this matter, I was not sure I could get it accurate in time
# makes the assumption the first 5 min of nexfin data is baseline
def sum_of_diffs(x, y, z):

    # is flopatch
    # y is nexfin
    # z indicates stage + 1, i.e. B = 1, 1 = 2, 2 = 3...
    # where x and y are formatted as attached data
    
    max = ((300 * z) - 1) - (x['TimeSec'].max())
    maxint = round(max.astype(int) * 1000)

    newnexfin = y[(y['TimeSec'] >= (300 * (z - 1 ))) & (y['TimeSec'] < (300 * z))]
    
    sums_diffs = []

    combined = pd.merge(left = x, right = newnexfin, on = 'TimeSec', how = 'right')

    for i in range(1, maxint):

        if i != 1: 
            combined['HR_x'] = combined['HR_x'].shift(1)
            no_nas = combined.dropna(subset='HR_x')
            hr_diffs = abs(no_nas['HR_x'].astype(int) - no_nas['HR_y'].astype(int))
            sums_diffs.append(sum(hr_diffs))
        else:
            no_nas = combined.dropna(subset = 'HR_x') # fix later, subset
            hr_diffs = abs(no_nas['HR_x'].astype(int) - no_nas['HR_y'].astype(int))
            sums_diffs.append(sum(hr_diffs))
    
    return(sums_diffs.index(min(sums_diffs)) / 1000)

if __name__ == '__main__':
    main()