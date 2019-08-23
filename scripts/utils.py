
# various utility functions related with rule mining

import numpy as np
import pickle, os
import re
from tqdm import tqdm

def topn(n, support_where):
        """
        n : (int)
        support_where : dictionary, key : subgraph_id, value : list of supporting news_ids
        Returns top n subgraphs that have the most support
        """
        supports = {}
        for k, v in support_where.items():
                supports[k] = len(v)
        sorted_x = sorted(supports.items(), key=lambda kv: kv[1])
        list_topn = sorted_x[-n:]
        list_topn.reverse()

        return list_topn

def sample_clusters(clusters):
        """
        clusters : dictionary, key : id, value : list of subgraph ids
        Given a dictionary of clusters, from each cluster, randomly samples one item
        """
        samples = {}
        for k, v in clusters.items():
                samples[k] = np.random.choice(v)

        return list(samples.values())

def filter_dict(d, keys):
        """
        d : dictionary
        keys : keys to be kept

        Returns filtered dictionary
        """
        return { key: d[key] for key in keys }

def save_graphs(subgraphs, samples, fname='subgraphs.pkl'):
        """
        subgraphs : dictionary, key : id, value : subgraph
        samples : ids to be kept
        fname : filename

        Saves pickle dump of subgraphs to 'fname'
        If samples is given, saves only those
        """
        res = {}
        if samples:
                for s in samples:
                        res[s] = subgraphs[s]

        else:
                res = subgraphs

        with open(fname, 'wb') as f:
                pickle.dump(res, f)

def reID(subgraphs, samples, freq_seqs, support_where, start_ID=0):
        """
        subgraphs : dictionary, key : id, value : subgraph
        samples : ids to be kept
        freq_seqs : dictionary of frequent sequences, key : id, value : sequence
        support_where : dictionary, key : subgraph_id, value : list of supporting news_ids
        start_ID : new ID's will start from this

        This function is used to modify ID's of given arguments
        Returns modified versions of them as a tuple
        """
        res = {}
        idmap = {samples[i] : start_ID + i for i in range(len(samples))}
        for sampleID in samples:
                subg = subgraphs[sampleID]
                subg.gid = idmap[sampleID]
                res[subg.gid] = subg

        resupport_where = {}
        for i in range(len(samples)):
                resupport_where[idmap[samples[i]]] = support_where[samples[i]]
                samples[i] = idmap[samples[i]]

        for k, seqs in tqdm(freq_seqs.items(), desc='Re-ID'):
                for j in range(len(seqs)):
                        seq = seqs[j]
                        reseq = []
                        for i in range(len(seq[0])):
                              reseq.append(idmap[seq[0][i]])
                        seqs[j] = tuple((tuple(reseq), seq[1]))

        return (res, samples, freq_seqs, resupport_where)

def save_month(subgraphs=None, rules=None, graphs=None, freq_seqs=None, support_where=None, name='month'):
        """
        subgraphs : dictionary, key : id, value : subgraph
        rules : found association rules 
        graphs : news graphs
        freq_seqs : dictionary of frequent sequences, key : id, value : sequence
        support_where : dictionary, key : subgraph_id, value : list of supporting news_ids
        name : filename to save to

        Saves information related to a month as pickle dump
        """
        if subgraphs:
                with open(name + '_subgraphs.pkl', 'wb') as f:
                        pickle.dump(subgraphs, f)
        if rules:
                with open(name + '_rules.pkl', 'wb') as f:
                        pickle.dump(rules, f)
        if graphs:
                with open(name + '_graphs.pkl', 'wb') as f:
                        pickle.dump(graphs, f)
        if freq_seqs:
                with open(name + '_freq_seqs.pkl', 'wb') as f:
                        pickle.dump(freq_seqs, f)
        if support_where:
                with open(name + '_support_where.pkl', 'wb') as f:
                        pickle.dump(support_where, f)

def partition_gspan_data(db_file, part_amounts, part_names):
        """
        db_file : database file, given in gSpan data format
        part_amounts : list of partition amounts
        part_names : list of partition names

        Given a database file, divides it into specified partitions
        Example : file contains 1000 items, part_amounts : [300, 400, 300]
                                            part_names   : [a, b, c]
                  will create 3 files named a, b, c,
                  containing 300, 400, 300 items(graphs) respectively
        """
        f = open(db_file, 'rb')
        
        part_id = 0
        for fname in tqdm(part_names, desc='Partitioning Months'):
                c = 0
                fmonth = open(fname + '.gspan.data', 'w')

                t_exp = r'^t # (?P<gid>[0-9]+)\n$'
                t_reg = re.compile(t_exp)
                
                while c <= part_amounts[part_id]:
                        line = f.readline()
                        match = re.match(t_reg, line.decode())
                        if match:
                                c += 1
                                if c > part_amounts[part_id]:
                                        f.seek(-len(line), 1)
                                        break
                        fmonth.write(line.decode())
                fmonth.write('t # -1')

                fmonth.close()
                part_id += 1

        f.close()

def partition_news_gspan():
        '''
        This function is specific to our data
        '''
        db_file = '../data/graph.gspan.data'
        part_amounts = [ 895,
                         831,
                         852,
                         955,
                         1016,
                         1077,
                         949,
                         874,
                         828,
                         1015,
                         1394,
                         1308 ]

        part_names   = [ 'january',
                         'february',
                         'march',
                         'april',
                         'may',
                         'june',
                         'july',
                         'august',
                         'september',
                         'october',
                         'november',
                         'december' ]

        partition_gspan_data(db_file, part_amounts, part_names)
