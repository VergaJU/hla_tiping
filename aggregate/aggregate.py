#!/usr/local/bin/python

import pandas as pd
import json
import sys

file_path = sys.argv[1]
sample = sys.argv[2]

arcas = pd.read_json(file_path+"/arcasHLA/"+sample+".genotype.json")
arcas["tool"] = "arcasHLA"


optitype= pd.read_csv(file_path+"/optitype/"+sample+"_result.tsv", sep="\t", index_col=[0])
optitype = optitype.drop(["Reads","Objective"],axis=1)

optitype = optitype.melt(var_name='columns', value_name='values')

# Separate the column names into 'A' and 'B' with numeric suffixes
optitype[['columns', 'index']] = optitype['columns'].str.extract(r'([A-Za-z]+)(\d+)')
optitype = optitype.pivot(index='index', columns='columns', values='values').reset_index(drop=True)
optitype["tool"] = "optitype"


t1k = pd.read_csv(file_path+"/t1k/T1K_"+sample+"_allele.tsv", sep=" ", header=None)
t1k = t1k.drop([1], axis=1)

# Remove "HLA-" from the strings
t1k[0] = t1k[0].str.replace('HLA-', '')

# Split the strings by "*" and expand them into separate columns
t1k[1] = t1k[0].str.split('*', expand=True)[0]

# Set column names
t1k.columns = ['Allele', 'Type']
t1k['Group'] = t1k.index % 2
t1k =  t1k.pivot_table(index='Group', columns='Type', values='Allele', aggfunc=lambda x: x).reset_index(drop=True)

t1k["tool"] = "T1K"

df = pd.concat([arcas, optitype,t1k], ignore_index=True)
df.index = df["tool"]
df = df.drop("tool", axis=1)
df.to_csv(file_path+"/aggregate_genotypes.tsv", sep ='\t')
