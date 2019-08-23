
# Library of functions related to association rule mining on graph databases

import numpy as np
from itertools import combinations
from collections import OrderedDict
import apyori
from pymining import seqmining
import utils as utils
from tqdm import tqdm
from datetime import datetime
import csv
import pickle
import math

def _allSubsets(s):
        """
        Recursively return all subsets of a given set
        Should not be used on a large set,
        too many recursive calls fill up the stack
        """
        if len(s) == 0:
                return []
        ps = _allSubsets(s[1:])
        return [(s[0],)] + [(s[0],) + p for p in ps] + ps

def _calcSupport(itemset, support_where):
        """
        Given a set of items and the support_where
        calculates the support of the set
        support_where : {subgraph_id(int) : supporting_graph_ids(set of ints)}
        The return value is the collective support
        meaning the supporting graphs contain all subgraphs in the itemset
        """
        if len(itemset) < 1:
                return 0
        _gidfirst = itemset[0]
        acc = set(support_where[_gidfirst])
        for item_gid in itemset[1:]:
                acc = acc.intersection(support_where[item_gid])
        return len(acc)

# For all apriori related functions, refer to :
# Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
# found http://www.rsrikant.com/papers/vldb94_rj.pdf
# These functions are present to give you more options for apriori method
# We have found apyori library works fine as well

def apriorigen(L, k):
        """
        Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
        Apriori candidate generation Sec. 2.1.1
        """
        Ck = set()
        for li in L:
                for lj in L:
                        if li == lj:
                                continue
                        candidate = set(li).union(lj)
                        if len(candidate) == k:
                                Ck.add(tuple(candidate))
        return Ck

def mineAssociationRules(support_where, minconf):
        """
        support_where : {subgraph_id(int) : supporting_graph_ids(set of ints)}
        minconf : minimum confidence(float)
        Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
        Sec. 3
        """
        foundRules = {}
        l = list(support_where.keys())
        k = len(l)
        for i in range(k-1):
                lk = combinations(l, k - i)
                for li in lk:
                        supp_l = _calcSupport(li, support_where)
                        genrules(li, li, supp_l, support_where, minconf, foundRules)

def mineAssociationRulesFaster(support_where, minconf):
        """
        Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
        Sec. 3.1
        """
        l = list(support_where.keys())
        k = len(l)
        foundRules = {}
        for i in range(k-1):
                lk = combinations(l, k - i)
                for li in lk:
                        H1 = genrules_singleconsequent(li, support_where, minconf, foundRules)
                        supp_l = _calcSupport(li, support_where)
                        ap_genrules(li, H1, supp_l, k, 1, support_where, minconf, foundRules)

        return foundRules

def ap_genrules(l, H, supp_l, k, m, support_where, minconf, foundRules):
        """
        Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
        Sec. 3.1
        """
        to_delete = set()
        if(k <= m + 1):
                return
        H_mp1 = apriorigen(H, m + 1)
        for h_mp1 in H_mp1:
                rule_from = set(l) - set(h_mp1)
                supp_a = _calcSupport(list(rule_from), support_where)
                if supp_a and (supp_l / supp_a) >= minconf:
                        dictkey = frozenset(rule_from)
                        if dictkey not in foundRules:
                                foundRules[dictkey] = [h_mp1]
                        elif h_mp1 not in foundRules[dictkey]:
                                foundRules[dictkey].append(h_mp1)
                        else:
                                to_delete.add(h_mp1)
                                continue
                        to_delete.add(h_mp1)
                        #print("{}\t=>\t{}".format(tuple(rule_from), h_mp1))
        ap_genrules(l, list(set(H_mp1) - to_delete), supp_l, k, m+1, support_where, minconf, foundRules) 
   
def genrules(l, a, supp_l, support_where, minconf, foundRules):
        """
        Fast Algorithms for Mining Association Rules, Agrawal R., Srikant R.
        Sec. 3
        """
        m = len(a)
        A = list(combinations(a, m - 1)) # m-1 itemsets
        for a in A:
                supp_a = _calcSupport(a, support_where)
                if supp_a and (supp_l / supp_a) >= minconf:
                        #print("{} => {}, conf:{}".format(a, set(l) - set(a), supp_l/supp_a))
                        rule_to = set(l) - set(a)
                        if a not in foundRules:
                                foundRules[a] = [rule_to]
                        elif rule_to not in foundRules[a]:
                                foundRules[a].append(rule_to)
                        else:
                                continue
                        #print("{}\t=>\t{}".format(a, rule_to))
                        if m-1 > 1:
                                genrules(l, a, supp_l, support_where, minconf, foundRules)

def genrules_singleconsequent(l, support_where, minconf, foundRules):
        """
        Find rules that have a single consequent only
        A => B, where A, B are sets and B has only 1 element
        results match with apyori library
        """
        consequents = set()
        for single in l:
                others = list(set(l) - set([single]))
                supp_a = _calcSupport(others, support_where)
                supp_l = _calcSupport(l, support_where)
                if supp_a and (supp_l / supp_a) >= minconf:
                        dictkey = frozenset(others)
                        if dictkey not in foundRules:
                                foundRules[dictkey] = [single]
                        elif single not in foundRules[dictkey]:
                                foundRules[dictkey].append(single)
                        else:
                                continue
                        consequents.add(single)
                        #print("{}\t=>\t{}".format(others, single))

        return [[x] for x in list(consequents)]

def getTransactions(support_where, transaction_count):
        """
        support_where : {subgraph_id(int) : supporting_graph_ids(set of ints)}
        Given support_where and how many transactions there are
        Returns transactions {transaction_id(int) : subgraph_ids(list of ints)}
        Each transaction is a seperate news and its subgraphs
        """
        records = [[] for i in range(transaction_count)]
        for k, v in support_where.items():
                for tid in list(v):
                        records[tid].append(k)

        return records

def getSequences(gs, samples=None, days=1):
        """
        Returns sequences of subgraphs
        This sequence consists of subgraph IDs and are char (pymining works on chars)
        gs is gSpan object
        Samples specify which subgraphs should be considered (rest are filtered)
        days attribute specify how long (in terms of time) our sequences should cover
        For example: 7 days means sequence consists of the subgraphs seen in a week in order
        """
        support_where = {}
        for sg in gs.subgraphs.values():
                support_where[sg.gid] = gs.support_where[sg.gid]
        if samples:
                support_where = utils.filter_dict(support_where, samples)
        records = getTransactions(support_where, len(gs.graphs))

        # Need to modify following arguments for different months
        # jan : 0, feb : 895, mar : 1726, apr : 2578, may : 3533,
        # jun : 4549, jul : 5626, aug : 6575, sep : 7449,
        # oct : 8277, nov : 9292, dec : 10686
        # TODO: Embed date attribute to nodes in the database,
        #       get them directly instead of needing these values
        dates = _getDates(0, 0 + len(gs.graphs))
        # group by days
        group_count = math.ceil((max(dates) / days) + 1)
        groups = {x:[] for x in range(group_count)}

        for i in range(len(dates)):
                groups[math.floor(dates[i] / days)].append(i)

        sequences = []
        for k, v in groups.items():
                seq = []
                for trans_id in v:
                        trans = records[trans_id]
                        for subgid in trans:
                                seq.append(subgid)

                # convert to char for pymining
                sequences.append("".join([chr(x) for x in seq]))
                #print("Sequence {}: {}".format(k, seq))

        return sequences

def frequentSequences(gs, samples=None, minsup=None, window_len=3, days=1, granularity=None):
        """
        Returns frequent sequences mined using pymining
        gs : gSpan object
        minsup : minimum support to decide for frequency of a sequence
                 ([1,2,1,3], [5,1,1,5]) with minsup=2 will return [1,1]
        window_len : specifies how many sequences are in a window
        days : used for getting sequences, check getSequences for detail
        granularity : is the "speed"(or step) of the window

        Example : window_len=7 days=1
                  The sequences will be daily subgraphs and window of 7
                  will act like a week
        """
        seqs = getSequences(gs, samples, days)

        # "Defaults" to window
        if not granularity:
                granularity = window_len
        if not minsup:
                minsup = window_len

        res = OrderedDict()
        freq_id = 0
        window_start = 0
        window_end   = window_len
        while window_end < len(seqs):
                window = seqs[window_start:window_end]
                freq_seqs = seqmining.freq_seq_enum(window, minsup)

                # chr to int conversion
                res[freq_id] = []
                for fseq in freq_seqs:
                        seq_items = []
                        for i in fseq[0]:
                                seq_items.append(ord(i))
                        res[freq_id].append((tuple(seq_items), fseq[1]))

                window_start += granularity
                window_end += granularity
                #print("Window {}: {}".format(freq_id, res[freq_id]))
                freq_id += 1

        return res

def print_rules(relations):
        """
        Used to print rules mined using apyori
        """
        for record in relations:
                for ordered in record.ordered_statistics:
                        ante  = list(ordered.items_base)
                        conse = list(ordered.items_add)
                        print("{}\t=>\t{}".format(ante, conse))

def mineApyori(gs, **kwargs):
        """
        Mine association rules using apyori library
        min_support, min_confidence, min_lift and max_length are apyori arguments
        show_rules is a boolean flag to decide if rules will be printed to screen
        samples may be specified to indicate which news we want to keep and rest are filtered
        if samples is None, all news will get considered
        """
        apyoriKwargs = {}
        min_support = kwargs.get('min_support', 1e-4)
        min_confidence = kwargs.get('min_confidence', 0.0)
        min_lift = kwargs.get('min_lift', 0.0)
        max_length = kwargs.get('max_length', None)
        show_rules = kwargs.get('show_rules', True)
        samples = kwargs.get('samples', None)

        apyoriKwargs['min_support'] = min_support
        apyoriKwargs['min_confidence'] = min_confidence
        apyoriKwargs['min_lift'] = min_lift
        apyoriKwargs['max_length'] = max_length

        support_where = {}
        for sg in gs.subgraphs.values():
                support_where[sg.gid] = gs.support_where[sg.gid]
        if samples:
                support_where = utils.filter_dict(support_where, samples)
        records = getTransactions(support_where, len(gs.graphs))
        gen = apyori.apriori(records, **apyoriKwargs)

        if show_rules:
                print_rules(gen)

        return gen

def mineApyoriSequences(windows, **kwargs):
        """
        Mine association rules from frequent sequences using apyori library
        min_support, min_confidence, min_lift and max_length are apyori arguments
        show_rules is a boolean flag to decide if rules will be printed to screen
        save_rules is a boolean flag to decide if rules will be saved to a file
        
        Note: since rules are a generator, show and save can not be done at the same time
        """
        apyoriKwargs = {}
        min_support = kwargs.get('min_support', 1e-4)
        min_confidence = kwargs.get('min_confidence', 0.0)
        min_lift = kwargs.get('min_lift', 0.0)
        max_length = kwargs.get('max_length', None)
        show_rules = kwargs.get('show_rules', False)
        save_fname = kwargs.get('save_rules', None)     # filename if not None

        apyoriKwargs['min_support'] = min_support
        apyoriKwargs['min_confidence'] = min_confidence
        apyoriKwargs['min_lift'] = min_lift
        apyoriKwargs['max_length'] = max_length

        i = 0
        records = [[] for x in range(len(windows))]
        for k, v in windows.items():
                for seq in v:
                        records[i].append(seq[0])
                i += 1
        gen = apyori.apriori(records, **apyoriKwargs)

        if show_rules and not save_fname:
                print_rules(gen)

        if save_fname:
                save_rules(gen, save_fname)

        return gen

def mineRulesFromSequences(freq_seqs, support_where, minconf):
        '''
        freq_seqs : dictionary of frequent sequences, key : id, value : sequence
        support_where : {subgraph_id(int) : supporting_graph_ids(set of ints)}
        From each sequence, try to generate a single rule
        Randomly divide the sequence into (A => B) Antecedent(A) and Consequent(B)
        Check if an association rule is formed or not
        '''
        foundRules = {}
        for k, v in tqdm(freq_seqs.items(), desc='Mining Rules'):
                for seq in v:
                        if len(seq[0]) > 1:
                                split_loc = np.random.randint(1, len(seq[0]))
                                ante = seq[0][:split_loc]
                                cons = seq[0][split_loc:]
                                supp_ante = _calcSupport(ante, support_where)
                                supp_cons = _calcSupport(cons, support_where)
                                if supp_ante and (supp_cons / supp_ante) >= minconf:
                                        dictkey = ante
                                        if dictkey not in foundRules:
                                                foundRules[dictkey] = [cons]
                                        elif cons not in foundRules[dictkey]:
                                                foundRules[dictkey].append(cons)

        return foundRules

def save_rules(gen, fname):
        """
        Given generator object (possibly from apyori output) and a filename
        Save found rules into file
        """
        f = open(fname, 'wb')
        all_rules = []
        for record in gen:
                for ordered in record.ordered_statistics:
                        ante  = list(ordered.items_base)
                        conse = list(ordered.items_add)
                        all_rules.append((ante, conse))
                        print(len(all_rules))
                        if(len(all_rules) > 1000):      # flush
                                pickle.dump(all_rules, f)
                                all_rules = []
        f.close()

def _getDates(start_idx=0, count=0):
        """
        This function reads from dates.csv given where to start and how many to read
        TODO: Update this function to get dates from db
        """
        dates = []
        with open("../data/dates.csv", "r") as fdates:
                dates_csv = csv.DictReader(fdates, fieldnames=["date"])
                next(dates_csv) # skip header
                for row in dates_csv:
                        d = [int(x) for x in row["date"].split("-")]
                        dates.append((datetime(*d) - datetime(1970, 1, 1)).days)

        # Starting day will be 0, we only need difference not exact date
        min_date = dates[start_idx]
        for i in range(start_idx, len(dates)):
                dates[i] -= min_date

        return dates[start_idx:count]
