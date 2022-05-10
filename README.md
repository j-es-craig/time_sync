# Flosonics Medical Techincal Task - Joshua Craig
## Scripts for syncing, plotting, and analyzing flopatch and nexfin data
## There are 3 scripts in this directory: 

`sync.py` will take one flopatch and one nexfin file, sync them, and output a single synced file

`make_plots.py` will plot time aligned nexfin and flopatch data for specified columns and save a `jpg` in the working directory. defaults are flopatch Vmax VTI Total and nexfin CO

`analysis.py` will output summary statistics, a summary of the OLS regression model, and plot the regression and qq plot. defaults are flopatch Vmax VTI total and nexfin CO

passing the `-h` flag for any script will print its help message.

running each script with no arguments will yield the expected deliverables as outlined in the PDF, i.e.:

`python .\sync.py`

`python .\make_plots.py`

`python .\analysis.py`

All expected outputs are in the `expected_deliverables` folder.

approximate runtime for `sync.py` is 20 - 30 minutes. 

NB: flopatch data has been converted from xls to csv, and renamed `fpdata_reformat.csv`