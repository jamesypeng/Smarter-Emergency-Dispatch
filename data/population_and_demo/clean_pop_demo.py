import pandas as pd
from os import listdir

def clean_pop_demo():
	dirs = [d + "/" for d in listdir() if d.startswith("sf_pop")]
	data_files = []
	suffix = ".csv"
	bad_word = "metadata"

	# Iterate through directories to assemble list of paths to files we want to parse
	for d in dirs:
	    files = [f for f in listdir(d) if f.endswith(suffix) and bad_word not in f]
	    for f in files:
	        data_files.append(d + f)

	df = pd.DataFrame()

	for d in data_files:
	    # parse year from filename
	    end = d.find("/ACS")
	    start = end - 4
	    year = d[start:end]

	    if year == '2015':
	        cols_df = pd.read_csv(d, header=1, usecols=[i for i in range(327)])
	        cols = list(cols_df.columns)
	        cols.append("Year")
	    
	    # read csv & get correct columns
	    new_df = pd.read_csv(d, header=None, skiprows=[0, 1], usecols=[i for i in range(327)])
	    new_df["Year"] = year

	    # Conditional check for proper concatenation
	    if df.empty:
	        df = new_df
	    else:
	        df = pd.concat([df, new_df], axis=0, ignore_index=True)

	df.columns = cols 
	df.to_csv("agg_pop_demo_data.csv")


if __name__ == "__main__":
	clean_pop_demo()