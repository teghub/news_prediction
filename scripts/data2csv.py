#!/usr/bin/env python3

# This script reads news-word relationship data and generates
# csv files to be imported to the graph database

import csv, sys, re
from tqdm import tqdm
import numpy as np

# data paths
datafile_path = "../data/"
wne_path = datafile_path + "news_word_ne.csv"
nn_path  = datafile_path + "news.csv"
ne_path  = datafile_path + "named_entities.csv"
wn_path  = datafile_path + "words.csv"
nwr_path = datafile_path + "nwr.csv"
wwr_path = datafile_path + "wwr.csv"
newr_path = datafile_path + "newr.csv"

# fields
wne_fields  = ["nid:ID", "word", "NamedEntity"]
nn_fields   = ["nid:ID", ":LABEL", "label"]
ne_fields   = ["neid:ID", ":LABEL", "name"]
wn_fields   = ["wid:ID", ":LABEL", "word"]
nwr_fields  = ["from:START_ID", "to:END_ID", ":TYPE"]
wwr_fields  = ["from:START_ID", "to:END_ID", ":TYPE", "contained_in:INT[]"]
newr_fields = ["from:START_ID", "to:END_ID", ":TYPE"]

# Names of all the named entities
named_entities = ["ORGANIZATION",
                  "LOCATION",
                  "PERSON",
                  "PERCENT",
                  "MONEY",
                  "DATE",
                  "TIME",
                  "OTHER"]

words = {}              # word : wid
named_entity_set = {}   # neid : set(wid)
news_words = {}         # nid  : set(wid)
words_order = {}        # nid  : list(wid)
news = []               # all news info after DictReader
dictWordRelations = {}  # (startid, endid) : set(nid)

_id = 0         # each node has unique id
dictNewsIds = {}

if __name__ == "__main__":
        # open files
        wnefile  = open(wne_path, "r")
        nnfile   = open(nn_path, "w+")
        nefile   = open(ne_path, "w+")
        wnfile   = open(wn_path, "w+")
        nwrfile  = open(nwr_path, "w+")
        wwrfile  = open(wwr_path, "w+")
        newrfile = open(newr_path, "w+")

        # dict read/writes
        wne  = csv.DictReader(wnefile, fieldnames=wne_fields)
        nn   = csv.DictWriter(nnfile, fieldnames=nn_fields)
        ne   = csv.DictWriter(nefile, fieldnames=ne_fields)
        wn   = csv.DictWriter(wnfile, fieldnames=wn_fields)
        nwr  = csv.DictWriter(nwrfile, fieldnames=nwr_fields)        
        wwr  = csv.DictWriter(wwrfile, fieldnames=wwr_fields)
        newr = csv.DictWriter(newrfile, fieldnames=newr_fields)

        # Write Headers
        nn.writeheader()
        ne.writeheader()
        wn.writeheader()
        nwr.writeheader()
        wwr.writeheader()
        newr.writeheader()

        next(wne)       # discard header

        for i in range(len(named_entities)):
                named_entity_set[i] = set()
                nedata = [_id, "NamedEntity", named_entities[i]]
                ne.writerow(dict(zip(ne_fields, nedata)))
                _id += 1

        for row in tqdm(wne):
                if not row["nid:ID"] in dictNewsIds:
                        # Sampling, uncomment following 2 lines to do so
                        #if int(row["nid:ID"]) == 15000:
                        #        break

                        nid = _id
                        dictNewsIds[row["nid:ID"]] = nid
                        newsdata = [nid, "News", 'news']
                        nn.writerow(dict(zip(nn_fields, newsdata)))
                        news_words[nid]  = set()
                        words_order[nid] = list()
                        _id += 1

                word = row["word"]
                if word not in words:
                        words[word] = _id
                        wndata = [_id, "Word", word]
                        wn.writerow(dict(zip(wn_fields, wndata)))
                        _id += 1
                        nid = dictNewsIds[row["nid:ID"]]
                words_order[nid].append(words[word])
                news_words[nid].add(words[word])
                # assign the word to its named entity
                neidx = named_entities.index(row['NamedEntity'])
                if not words[word] in named_entity_set[neidx]:
                        named_entity_set[neidx].add(words[word])

        # write news - words relationship
        i = 0
        for nid, word_ids in news_words.items():
                i += 1		
                for word_id in word_ids:
                        nwrdata = [nid, word_id, "CONTAINS"]
                        nwr.writerow(dict(zip(nwr_fields, nwrdata)))

        for k, nid in dictNewsIds.items():
                for i in range(len(words_order[nid])-1):
                        if (words_order[nid][i], words_order[nid][i+1]) in dictWordRelations:
                                dictWordRelations[(words_order[nid][i], words_order[nid][i+1])].add(nid)
                        else:
                                dictWordRelations[(words_order[nid][i], words_order[nid][i+1])] = set([nid])

        for neid, new in named_entity_set.items():
                for word_id in new:
                        newrdata = [word_id, neid, "IS"]
                        newr.writerow(dict(zip(newr_fields, newrdata)))

        for k, v in dictWordRelations.items():
                varray = ";".join(list(map(str,v)))
                wwrdata = [k[0], k[1], "FOLLOWED_BY", varray]
                wwr.writerow(dict(zip(wwr_fields, wwrdata)))

        # close files
        wnefile.close()
        nnfile.close()
        nefile.close()
        wnfile.close()
        nwrfile.close()
        wwrfile.close()
        newrfile.close()
