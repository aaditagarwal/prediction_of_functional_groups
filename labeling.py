from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit.Chem import rdmolfiles
from rdkit import RDLogger
from os import listdir
import numpy as np
import pandas as pd

#Disablingerror by RDkit for inbalanced valences in atoms
lg = RDLogger.logger()
lg.setLevel(RDLogger.CRITICAL)

#Defining Smarts Values for comparision and identification of functional groups
smarts = {}
smarts['Alkane'] = '[CX4]'
smarts['Alkene'] = '[$([CX3]=[CX3])]'
smarts['Alkyne'] = '[$([CX2]#C)]'
smarts['Aromatic'] = '[c]'
smarts['Carboxylic acid'] = '[CX3](=O)[OX2H1]'
smarts['Ester'] = '[#6][CX3](=O)[OX2H0][#6]'
smarts['Ketone'] = '[#6][CX3](=O)[#6]'
smarts['Aldehyde'] = '[CX3H1](=O)[#6]'
smarts['Anhydride'] = '[CX3](=[OX1])[OX2][CX3](=[OX1])'
smarts['Acyl Halide'] = '[CX3](=[OX1])[F,Cl,Br,I]'
smarts['Ether'] = '[OD2]([#6])[#6]'
smarts['Nitrile'] = '[NX1]#[CX2]'
smarts['Alcohol'] = '[#6][OX2H]'


#Obtaining mol structures from the smarts
smarts_mol = {}
for key,value in smarts.items():
    try:
        smarts_mol[key] = Chem.MolFromSmarts(value)
    except:
        print('Cannot convert to mol for ',key)
        smarts_mol[key] = None

#Comparing the .mol data files with the substructures to obtain possible functional groups present in the compound
files = [f for f in listdir('./Obj1_data/mol') if f.find('.mol')]
labels = np.zeros((len(files),len(smarts_mol)))
for i,file in enumerate(files):
    try:
        mol_file = rdmolfiles.MolFromMolFile('./Obj1_data/mol/'+file)
    except:
        print('Unable to retrieve ',file,'.mol file')
        mol_file = None
    for j,smart in enumerate(smarts_mol.items()):
        if smart[1] != None and mol_file != None: 
            if mol_file.HasSubstructMatch(smart[1]): 
                labels[i,j] = 1

#Creating a DataFrame for the labels array
labels_df = pd .DataFrame(labels,index=files,columns=smarts.keys())

#Removing molecules which have no identified functional groups
sum_MOL = labels_df.sum(axis=1)
labels_df = labels_df.loc[sum_MOL[sum_MOL!=0].index,:]

#Removing functional groups with less than 15 occurances
sums = labels_df.sum(axis=0)
labels_df = labels_df.loc[:,sums > 15]

#Exporting labels dataframe to excel for further use
labels_df.to_excel('./Obj1_data/labels.xlsx')