#!/usr/bin/env python3

import os,sys,inspect
import graphOneHotEncoding as gohe
from converter import gSpan2query
import pickle
from tqdm import tqdm

dirname = '../data/months/prediction/'
train_months   = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november']
predict_months = ['december']

subgraph_ranges = {}    # range : 'month_name'

def gather_subgraphs():
        """
        Read subgraphs from both train and prediction months and return them together
        Also fills subgraph ranges
        """
        res = {}
        train_subgraphs   = []
        predict_subgraphs = []
        for month in tqdm(train_months, desc='Reading Train Subgraphs'):
                with open(dirname + month + '_subgraphs.pkl', 'rb') as f:
                        subgraphs = pickle.load(f)
                        subgraph_ranges[range(min(subgraphs), max(subgraphs)+1)] = month
                        train_subgraphs.append(subgraphs)

        for month in tqdm(predict_months, desc='Reading Predict Subgraphs'):
                with open(dirname + month + '_subgraphs.pkl', 'rb') as f:
                        subgraphs = pickle.load(f)
                        subgraph_ranges[range(min(subgraphs), max(subgraphs)+1)] = month
                        predict_subgraphs.append(subgraphs)

        for d in train_subgraphs:
                res.update(d)

        for d in predict_subgraphs:
                res.update(d)

        return res

def gather_rules():
        """
        Read rules found from train months and return them
        """
        res = {}
        rules = []
        for month in tqdm(train_months, desc='Reading Rules'):
                with open(dirname + month + '_rules.pkl', 'rb') as f:
                        rules.append(pickle.load(f))

        for d in rules:
                res.update(d)

        return res

def gather_sequences():
        """
        Read sequences found from prediction months and return them
        """
        res = {}
        sequences = []
        for month in tqdm(predict_months, desc='Reading Sequences'):
                with open(dirname + month + '_freq_seqs.pkl', 'rb') as f:
                        sequences.append(pickle.load(f))

        for d in sequences:
                res.update(d)

        return res

def predict(sequence, rules, ratio=0.9):
        """
        sequence : list of ids
        rules : dictionary, key : antecedent (list of ids), consequents (list of sequences)
        ratio : how similar sequence must be to a rule antecedent to be predicted

        Given a sequence, rules and ratio, for each rule,
        first get all candidates having same length antecedent as the sequence
        then, check cosine similarity in the order of the sequence and candidate
        If similarity is above the ratio, append the consequent to predictions
        Return predictions
        """
        predictions = []
        candidates = {k:v for k, v in rules.items() if len(k) == len(sequence)}
        for candidate in candidates:
                sim = 1.0
                for i in range(len(sequence)):
                        sim *= gohe.get_cosine_sim(sequence[i], candidate[i])
                if sim >= ratio:
                        for cons in candidates[candidate]:
                                predictions.append(cons)

        return predictions

if __name__ == "__main__":
        # Read files and init gohe
        subgraphs = gather_subgraphs()
        rules     = gather_rules()
        sequences = gather_sequences()
        gohe._init_gohe(subgraphs)

        # Check for similarities in antecedent of sequences and rules
        predictions = {}
        all_sequences = set([seq[0] for seqlist in sequences.values() for seq in seqlist]) 
        for sequence in tqdm(all_sequences, desc='Prediction'):
                pred = predict(sequence, rules, 0.725)
                if pred:
                        predictions[sequence] = pred

        # Write predictions into a file
        with open('predictions.pkl', 'wb') as f:
                pickle.dump(predictions, f)
