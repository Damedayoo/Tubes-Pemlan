# -*- coding: utf-8 -*-
"""Tubes : Best Model for Loan_Predict.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mvv1-OwiApQjz20oYp0H838810GqL0oe

# Import Library
"""

import os #paths to file
import numpy as np # linear algebra
import pandas as pd # data processing
import warnings# warning filter


#ploting libraries
import matplotlib.pyplot as plt
import seaborn as sns

#relevant ML libraries
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score

#ML models
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

#default theme
sns.set(context='notebook', style='darkgrid', palette='deep', font='sans-serif', font_scale=1, color_codes=False, rc=None)

#warning hadle
warnings.filterwarnings("ignore")

"""# Preprocessing Data and Data Analysis

## First look at the data:

Training set:
"""

# read in csv file as a DataFrame
tr_df = pd.read_csv("loan_train.csv")
# explore the first 5 rows
tr_df.head()

"""Testing set:"""

# read in csv file as a DataFrame
te_df = pd.read_csv("loan_test.csv")
# explore the first 5 rows
te_df.head()

"""Size of each data set:"""

print(f"training set (row, col): {tr_df.shape}\ntesting set (row, col): {te_df.shape}")

"""### Preprocessing of the training dataset."""

#column information
tr_df.info(verbose=True, null_counts=True)

#summary statistics
tr_df.describe()

#the Id column is not needed, let's drop it for both test and train datasets
tr_df.drop('Loan_ID',axis=1,inplace=True)
te_df.drop('Loan_ID',axis=1,inplace=True)
#checking the new shapes
print(f"training set (row, col): {tr_df.shape}\n\ntesting set (row, col): {te_df.shape}")

"""## Missing values
Melihat berapa banyak missing values dari tiap kolom
"""

#missing values in decsending order
tr_df.isnull().sum().sort_values(ascending=False)

"""Setiap nilai akan diganti dengan nilai yang paling sering muncul (modus)."""

#filling the missing data
print("Before filling missing values\n\n","#"*50,"\n")
null_cols = ['Credit_History', 'Self_Employed', 'LoanAmount','Dependents', 'Loan_Amount_Term', 'Gender', 'Married']


for col in null_cols:
    print(f"{col}:\n{tr_df[col].value_counts()}\n","-"*50)
    tr_df[col] = tr_df[col].fillna(
    tr_df[col].dropna().mode().values[0] )


tr_df.isnull().sum().sort_values(ascending=False)
print("After filling missing values\n\n","#"*50,"\n")
for col in null_cols:
    print(f"\n{col}:\n{tr_df[col].value_counts()}\n","-"*50)

"""## Data visalization

membagi data menjadi data categorical dan numerik

## Loan status distribution
"""

#list of all the columns.columns
#Cols = tr_df.tolist()
#list of all the numeric columns
num = tr_df.select_dtypes('number').columns.to_list()
#list of all the categoric columns
cat = tr_df.select_dtypes('object').columns.to_list()

#numeric df
loan_num =  tr_df[num]
#categoric df
loan_cat = tr_df[cat]

print(tr_df[cat[-1]].value_counts())

total = float(len(tr_df[cat[-1]]))
plt.figure(figsize=(8, 10))
sns.set(style="whitegrid")
ax = sns.countplot(x=cat[-1], data=tr_df)  # Perubahan di sini, tambahkan x=cat[-1]
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x() + p.get_width() / 2., height + 3, '{:1.2f}'.format(height/total), ha="center")
plt.show()

"""Plot data

- Numeric:
"""

for i in loan_num:
    plt.hist(loan_num[i])
    plt.title(i)
    plt.show()

"""- Categorical (split by Loan status):"""

for i in cat[:-1]:
    plt.figure(figsize=(15,10))
    plt.subplot(2,3,1)
    sns.countplot(x=i ,hue='Loan_Status', data=tr_df ,palette=['limegreen', 'darkgreen'])
    plt.xlabel(i, fontsize=14)

"""## Encoding data to numeric"""

# Mapping categorical values to numeric representations
label_mapping = {
    'Male': 1, 'Female': 2,
    'Yes': 1, 'No': 2,
    'Graduate': 1, 'Not Graduate': 2,
    'Urban': 3, 'Semiurban': 2, 'Rural': 1,
    'Y': 1, 'N': 0,
    '3+': 3
}

# Applying label mapping to both datasets
tr_df = tr_df.applymap(lambda label: label_mapping.get(label) if label in label_mapping else label)
te_df = te_df.applymap(lambda label: label_mapping.get(label) if label in label_mapping else label)

# Converting the 'Dependents' column to numeric
tr_df['Dependents'] = pd.to_numeric(tr_df['Dependents'])
te_df['Dependents'] = pd.to_numeric(te_df['Dependents'])

# Checking the shape and information of the manipulated datasets
print(f"Training set dimensions: {tr_df.shape}\nTesting set dimensions: {te_df.shape}\n")
print("Training set information:\n", tr_df.info(), "\n\nTesting set information:\n", te_df.info())

"""## Matrix Korelasi"""

#plotting the correlation matrix
sns.heatmap(tr_df.corr() ,cmap='cubehelix_r')



"""### Tabel korelasi"""

#correlation table
corr = tr_df.corr()
corr.style.background_gradient(cmap='coolwarm').set_precision(2)

"""Kita dapat melihat dengan jelas bahwa `Loan_Status` memiliki korelasi tertinggi dengan `Credit_History` (korelasi positif `0,54`).

# Machine learning models

Pertama-tama kita akan membagi dataset kita menjadi dua variabel `X` sebagai fitur yang kita definisikan sebelumnya dan `y` sebagai `Loan_Status` nilai target yang ingin kita prediksi.

## ML Model yang akan digunakan:

* **Decision Tree**
* **Random Forest**
* **XGBoost**
* **Logistic Regression**
"""

y = tr_df['Loan_Status']
X = tr_df.drop('Loan_Status', axis = 1)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 0)

"""## Decision Tree

"""

DT = DecisionTreeClassifier()
DT.fit(X_train, y_train)

y_predict = DT.predict(X_test)

#  prediction Summary by species
print(classification_report(y_test, y_predict))

# Accuracy score
DT_SC = accuracy_score(y_predict,y_test)
print(f"{round(DT_SC*100,2)}% Accurate")

Decision_Tree=pd.DataFrame({'y_test':y_test,'prediction':y_predict})
Decision_Tree.to_csv("Dection Tree.csv")

"""Didapat output file Dection Tree.csv

## Random Forest
"""

RF = RandomForestClassifier()
RF.fit(X_train, y_train)

y_predict = RF.predict(X_test)

#  prediction Summary by species
print(classification_report(y_test, y_predict))

# Accuracy score
RF_SC = accuracy_score(y_predict,y_test)
print(f"{round(RF_SC*100,2)}% Accurate")

Random_Forest=pd.DataFrame({'y_test':y_test,'prediction':y_predict})
Random_Forest.to_csv("Random Forest.csv")

"""Didapat output file Random Forest.csv

## XGBoost
"""

XGB = XGBClassifier()
XGB.fit(X_train, y_train)

y_predict = XGB.predict(X_test)

#  prediction Summary by species
print(classification_report(y_test, y_predict))

# Accuracy score
XGB_SC = accuracy_score(y_predict,y_test)
print(f"{round(XGB_SC*100,2)}% Accurate")

XGBoost=pd.DataFrame({'y_test':y_test,'prediction':y_predict})
XGBoost.to_csv("XGBoost.csv")

"""Didapat output file XGBoost.csv

## Logistic Regression
"""

LR = LogisticRegression()
LR.fit(X_train, y_train)

y_predict = LR.predict(X_test)

#  prediction Summary by species
print(classification_report(y_test, y_predict))

# Accuracy score
LR_SC = accuracy_score(y_predict,y_test)
print('accuracy is',accuracy_score(y_predict,y_test))

Logistic_Regression=pd.DataFrame({'y_test':y_test,'prediction':y_predict})
Logistic_Regression.to_csv("Logistic Regression.csv")

"""Didapat output file Logistic Regression.csv"""

score = [DT_SC,RF_SC,XGB_SC,LR_SC]
Models = pd.DataFrame({
    'n_neighbors': ["Decision Tree","Random Forest","XGBoost", "Logistic Regression"],
    'Score': score})
Models.sort_values(by='Score', ascending=False)