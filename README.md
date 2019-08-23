# GraphDB based Graph Mining Library for News Prediction and Recommendation
> **NOTE:** Please refer the paper in the src folder. This project is developed under the CENG488 course at METU and also the project which is funded by TUBITAK.

## Background

The task of extracting useful information from a large database is becoming increasingly challenging and important. When relationships are prioritized, it makes great sense to use a graph database thanks to performance improvements and flexibility. Various types of data can be represented using graphs. In this work, we are representing textual data as a graph. The proposed graph model produces a compact and informative representation of news content, allowing us to store sufficient amount of data while generating the results of database queries quickly. In order to simplify the process of working on such databases, we develop a Graph Mining Library that supports mining of frequent subgraphs, frequent sequences of these subgraphs, extraction of rules and calculation of similarities among subgraphs. gSpan algorithm is used to mine the frequent subgraphs. Frequent sequences are found using Apriori treating each subgraph as an item. Association rules are found by processing these frequent sequences based on a confidence threshold. By having collected association rules corresponding to a certain time period, we can make predictions for the next time slot. Frequent sequences are generated for the next time slot which are then tested for similarity against the antecedents of the rules previously found. Similarity match allows us to predict the consequent.

## Introduction

With the increasing use of the Internet, the public data is getting larger every day. In particular, news web sites and social media data make a big contribution to this pile of information. The structure of these sort of data contain many relationships, which makes a graph structure a good candidate for representation. Graph based structure of information simplifies representation of complex and abundant relationships between distinct entities as well as extraction of different types of information.

Within the scope of this project, we aim to develop a method that uses graph similarity and frequent subgraph mining techniques together in order to obtain informative rules by association rule mining. By graph similarity, we imply the structural correspondence of nodes and edges of two graphs. Notion of the similarity between graphs can be isomorphism, edit distance, maximum and minimum common subgraphs, and statistical comparison. Association rule mining on graphs finds the relationships between sets/sequences of subgraphs. These rules in turn, can uncover the hidden patterns in the data and can also be used for prediction purposes.

## Developers

* **M. Ege Çıklabakkal**, _Department of Computer Engineering, Middle East Technical University_
* **Mert Erdemir**, _Department of Computer Engineering, Middle East Technical University_

## Requirements

1) **py2neo:**  
    For python2:
    ```bash
        $ sudo -H pip install py2neo
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install py2neo
    ```
2) **tqdm:**  
    For python2:
    ```bash
        $ sudo -H pip install tqdm
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install tqdm
    ```
3) **NetworkX:**  
    For python2:
    ```bash
        $ sudo -H pip install networkx
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install networkx
    ```
4) **NumPy:**  
    For python2:
    ```bash
        $ sudo -H pip install numpy
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install numpy
    ```
5) **scipy:**  
    For python2:
    ```bash
        $ sudo -H pip install scipy
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install scipy
    ```
6) **Sci-kit Learn:**  
    For python2:
    ```bash
        $ sudo -H pip install sklearn
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install sklearn
    ```
7) **Matplotlib:**  
    For python2:
    ```bash
        $ sudo -H pip install matplotlib
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install matplotlib
    ```
8) **inspect:**  
    For python2:
    ```bash
        $ sudo -H pip install inspect
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install inspect
    ```
9) **apyori:**  
    For python2:
    ```bash
        $ sudo -H pip install apyori
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install apyori
    ```
10) **pymining:**  
    For python2:
    ```bash
        $ sudo -H pip install pymining
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install pymining
    ```
11) **datetime:**  
    For python2:
    ```bash
        $ sudo -H pip install datetime
    ```
    For python3:
    ```bash
        $ sudo -H pip3 install datetime
    ```
## Explanation of the Folders
1) **data** Folder:
This folder contains the dataset files and their versions for the different steps and usage. The existing data can be referred as an experimental data or testing data. The folder hierarchy should be preserved even if they are empty.
-  **graphs_csv** Folder: This folder contains the news document graphs in CSV file format and their possible (optional) attributes. The files are generated by the **extract_news_graphs.py** script.
- **months** Folder: This folder contains both monthly generated gSpan formatted graph data and also the required files for the prediction script.
- **All CSV** Files: Except the **news_raw.csv** file they are generated by **data2csv.py** script. These files can be used to import graph structure into the Neo4j Graph Database with **graph_creator.py** script. 
- **Zip** File: contains the test data of months folder.

2) **scripts** Folder:
- **graph4teghub** Folder: This folder contains the Graph class which is implemented in the scope of the project related to this library.
- **gSpan** Folder: This folder contains [the gSpan implementation](https://github.com/betterenvi/gSpan). However, we made a change in the codes. Please refer [this issue](https://github.com/betterenvi/gSpan/issues/9).
- **init.py** File: This file is used for library import operations.
- **converter.py** File: This file is used to generate frequent subgraphs, association rules and other required files for the prediction process.
- **csv2gspan.py** File: This file is used to convert Neo4j graph structure to the gSpan input format.
- **data2csv.py** File: This file is used to generate the input files of Neo4j Graph Database import operation.
- **extract_graph_attrs.py** File: This file is used to extract graph attributes from the **news_raw.csv** file.
- **extract_news_graphs.py** File: This file is used to extract the Neo4j Graph Database formatted news documents to **graphs_csv** folder in CSV file format. These are used as input files in **csv2gspan.py** script.
- **graph_creator.py** File: This file is used for import operation to Neo4j Graph Database. The input files are the CSV files in **data** folder.
- **graphEditDistance.py** File: This file consists of the Graph Edit Distance calculator class. This class is used to reduce the subgraphs in **converter.py** script.
- **graphOneHotEncoding.py** File: This file consists of the Graph One Hot Encoding implementation (Graph Embedding into Vector Space with One Hot Encoding). Its functions are used to reduce the subgraphs in **converter.py** script.
- **prediction.py** File: This file consists of the prediction functions. The logic behind the prediction is explained in both **Background** and **Introduction** sections.
- **ruleMining.py** File: This file contains the required rule mining functions. It is used in **converter.py** while extracting the rules between the frequent subgraphs.
- **utils.py** File: This file contains various utility functions related with rule mining. It is used in **ruleMining.py** and **converter.py**. 

## Usage

We have divided this section into several different subsections for example, Importing Data to Neo4j and Exporting for gSpan Algorithm, Using Converter Script for Rule Mining and Prediction. In this section, we explained how to use the scripts and their details as parameters. We didn't explain what is the logic behind the scripts. Just input-outputs and usage. Many of the scripts can be directly run as *"./<script_name>"*, make sure that they have executable rights.

### Importing Data to Neo4j and Exporting for gSpan Algorithm
In order to import the data into Neo4j Graph Database, whole data should be formatted and separated as the CSV files in the **data** folder. Therefore, generating these files can be achieved with **data2csv.py** script. Before running the script please check that **news_word_ne.csv** file exists in the **data** folder. To run the script:
```bash
$ ./data2csv.py
```
The generated csv files contain information about news nodes, named entities and relationships. They can be imported to Neo4j Graph Database using the script **graph_creator.py**. Database user and password information can be changed inside the script, by default they are set to *(neo4j, neo4j)*.
```bash
$ ./graph_creator.py
```
Now, we can export data from the database. For each news, nodes and relationships it has can be extracted using **extract_news_graphs.py** script. Once again, database user and password information can be changed inside the script, by default they are set to *(neo4j, neo4j)*.
```bash
$ ./extract_news_graphs.py
```
In order to mine subgraphs, gSpan is used. Input to gSpan must be in a special format, thus **csv2gspan.py** can be used to generate the gSpan data from the csv files. The gSpan data can be created from arbitrary portions of news nodes, meaning that you can generate the gSpan data of a week, a month, a year etc. The script takes two arguments, **start_nid** and **specified_count**. First one specified the starting news id, second one specifies how many news should be converted to gSpan format. So, if your data is already sorted in terms of date, and you know how many news exist for each month, then by specifying the correct arguments to the script, you can generate seperate gSpan input data for each month. Obviously, the script will be run seperately for each month in that case. If no argument is specified, all news are converted to gSpan format as a single file.
```bash
$ ./csv2gspan.py <start_nid> <specified_count>
```

### Using Converter Script for Rule Mining
Converter is where we mine frequent subgraphs using gSpan, mine frequent sequences and association rules from these sequences and save these information. Converter does not take arguments, however there are many values that may be modified from inside the script. Firstly, gSpan command requires minimum support, minimum nodes and data input arguments respectively. For more info on the command, look into [gSpan repository](https://github.com/betterenvi/gSpan).  
Many of the frequent subgraphs are too similar. These similar subgraphs do not convey useful information, thus we try to eliminate them by applying graph similarity and clustering subgraphs based on the similarity measures. In the function *gohe.get_clusters(gs.subgraphs, <threshold>)*, threshold value may be modified depending on your needs. If subgraphs are too similar, a higher threshold value may be suitable.  
After mining frequent subgraphs and reducing them, frequent sequences are mined *(rm.frequentSequences(gs, samples, 3, 7, 1, 1))*. These values may also be tweaked according to your experiments. For more info on the arguments, check the source code and comments.  
Lastly, mining rules (*rm.mineRulesFromSequences(freq_seqs, support_where, 0.8)*) also requires another threshold value.  

Converter script is used to save these mined subgraphs, sequences and rules. On our project, we have worked on months, thus lastly *save_month(...)* function is called to save these information as pickle files. However, they are not required to be months, this function can be used with any batch of information.  

An important event that takes place in this script is *reID*. When we have seperate input files (for each month) and we apply these mining procedures, we will always get subgraphs starting from ID of 0. However, for each input, we will get different subgraphs, thus their ID's need to be changed. Modifying *start_ID* argument of *reID* function, we specify from which value ID's should start. When converter finished executing, it will print the next start ID, so you can modify the source accordingly.
```bash
$ ./converter.py
```

### Prediction
Prediction script will read subgraphs, rules and sequences generated previously using **converter.py** and predict new rules for a month that has not been used as a train month. Source code can be modified to use weeks or years instead of months. *predict* function has a ratio argument that can be modified. A higher ratio means that found rules will be stronger than a lower ratio and usually results in fewer rules found.
```
$ ./prediction.py
```
