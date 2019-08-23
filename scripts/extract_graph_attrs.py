#! /usr/bin/env python3
"""
This script is used for extracting attributes for
the news documents. If graphs_csv file has already
contained attribute files change the graph_cnt variable
as:
    graph_cnt = int(len(os.listdir(ATTR_FOLDER))/3)

If There is no files in the graphs_csv folder change it to
any number of news. For example, if you want to get the very
1000 first news attributes:
    graph_cnt = 1000
    
You can change the needed attributes from the ATTR_FIELDS
variable.

NOTE: PLEASE CHECK THAT graphs_csv folder exists in the
data folder.
"""
import sys, os, csv, tqdm

COUNTER        = 0
CURR_DIR       = os.getcwd()
ATTR_FILE_NAME = 'news_raw.csv'
ATTR_FILE_PATH = os.path.join(CURR_DIR, '..', 'data', ATTR_FILE_NAME)
ATTR_FOLDER    = os.path.join(CURR_DIR, '..', 'data', 'graphs_csv')
ATTR_FIELDS    = ['date', 'title', 'firstParagraph', 'content']
graph_cnt      = int(len(os.listdir(ATTR_FOLDER))/2)

def main():
    global COUNTER
    ATTR_FILE  = open(ATTR_FILE_PATH, 'r')
    FIELDNAMES = ATTR_FILE.readline()[:-1].split(',')
    ATTR_CSV   = csv.DictReader(ATTR_FILE, fieldnames=FIELDNAMES)
    for row in tqdm.tqdm(ATTR_CSV, desc="Exporting Attributes"):
        if COUNTER == graph_cnt:
            break
        file_path = os.path.join(ATTR_FOLDER, 'graph_' + str(COUNTER) + '.attrs')
        COUNTER += 1
        with open(file_path, 'w+') as fp:
            new_row = {}
            for field in ATTR_FIELDS:
                new_row[field] = row[field]
            fp.write(str(new_row))

if (__name__ == "__main__"):
    main()