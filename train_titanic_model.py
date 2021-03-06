# -*- coding: utf-8 -*-
"""train_titanic_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JpukDp17h0SVmP08r1nooSvzcpF15syZ

# **1. Overview**

**The Challenge**

The sinking of the Titanic is one of the most infamous shipwrecks in history.

On April 15, 1912, during her maiden voyage, the widely considered “unsinkable” RMS Titanic sank after colliding with an iceberg. Unfortunately, there weren’t enough lifeboats for everyone onboard, resulting in the death of 1502 out of 2224 passengers and crew.

While there was some element of luck involved in surviving, it seems some groups of people were more likely to survive than others.

In this challenge, we ask you to build a predictive model that answers the question: “what sorts of people were more likely to survive?” using passenger data (ie name, age, gender, socio-economic class, etc).

The data has been split into two groups:

  1. training set (train.csv)
  2. test set (test.csv)

The training set should be used to build your machine learning models. For the training set, we provide the outcome (also known as the “ground truth”) for each passenger. Your model will be based on “features” like passengers’ gender and class. You can also use feature engineering to create new features.

The test set should be used to see how well your model performs on unseen data. For the test set, we do not provide the ground truth for each passenger. It is your job to predict these outcomes. For each passenger in the test set, use the model you trained to predict whether or not they survived the sinking of the Titanic.

**Variable Notes**


**pclass**: A proxy for socio-economic status (SES)
1st = Upper
2nd = Middle
3rd = Lower

**age**: Age is fractional if less than 1. If the age is estimated, is it in the form of xx.5

**sibsp**: The dataset defines family relations in this way...

**Sibling** = brother, sister, stepbrother, stepsister

**Spouse** = husband, wife (mistresses and fiancés were ignored)

**parch**: The dataset defines family relations in this way...

**Parent** = mother, father

**Child** = daughter, son, stepdaughter, stepson

Some children travelled only with a nanny, therefore parch=0 for them.

**NOTE:** Use google colab IDE to run this notebook

# **2. Import Libraries:**
"""

# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

"""# **3. Load Dataset:**"""

# upload the train dataset
from google.colab import files
uploaded=files.upload()

import io
titanic_df=pd.read_csv(io.StringIO(uploaded['train.csv'].decode('utf-8')))

titanic_df.head()

"""# **4.Exploratory Data Analysis:**"""

# shape of dataset
titanic_df.shape

# statistical analysis of train data
titanic_df.describe()

titanic_df.columns

titanic_df.info()

# check for null values
titanic_df.isnull().sum()

# fill null values of 'Age' column be median of that column
titanic_df['Age']=titanic_df['Age'].fillna(titanic_df['Age'].median())
# fill null values of 'Embarked' column be mode of that column
titanic_df['Embarked']=titanic_df['Embarked'].fillna(titanic_df['Embarked'].mode()[0])

# drop unnecessary columns
titanic_df.drop(columns=["Cabin","Name","Ticket","PassengerId"],axis=1,inplace=True )

# create a new column by adding 'Parch' & 'SibSp' columns
titanic_df["Family_Member"]=titanic_df['Parch']+titanic_df['SibSp']

# drop 'SibSp' & 'Parch' columns
titanic_df.drop(columns=["SibSp","Parch"],axis=1,inplace=True )

# check for null values
titanic_df.isnull().sum()

# separate columns having categorical values
object_df=titanic_df.select_dtypes(include=['object']).copy()
object_df.head()

object_df.nunique()

# unique values in object_df dataframe
print("Sex :",object_df.Sex.unique())
print("Embarked :",object_df.Embarked.unique())

"""# **5.Data Visualization:**"""

# visualize frequency distribution using barplot
def plot_bar_graph(column_name):
    ed_count = column_name.value_counts()
    sns.set(style="darkgrid")
    sns.barplot(ed_count.index, ed_count.values, alpha=0.9)
    plt.title('Frequency Distribution of {} Levels using Bar Plot'.format(column_name.name))
    plt.ylabel('Number of Occurrences', fontsize=12)
    plt.xlabel('{}'.format(column_name.name), fontsize=12)
    plt.show()

# visualize frequency distribution using pie chart
def plot_pie_graph(column_name):
    labels = column_name.astype('category').cat.categories.tolist()
    counts = column_name.value_counts()
    sizes = [counts[var_cat] for var_cat in labels]
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True) #autopct is show the % on plot
    ax1.axis('equal')
    plt.title('Frequency Distribution of {} Levels using Pie Chart'.format(column_name.name))
    plt.show()

for col in object_df.columns:
    plot_bar_graph(object_df[col])
    plot_pie_graph(object_df[col])

# separate columns having numeric values
int_df=titanic_df.select_dtypes(include=['integer']).copy()
int_df.drop(axis=1,columns=['Survived'],inplace=True)
int_df.head()

# distribution of 'Pclass' column
sns.distplot(int_df['Pclass'])

# distribution of 'Family_Member' column
sns.distplot(int_df['Family_Member'])

"""# **6.Data Preprocessing**"""

# encode the categorical values into numeric values
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()
for col in object_df.columns:
    titanic_df[col]=le.fit_transform(titanic_df[col])

titanic_df.head()

# co-relation of columns with eachother
plt.figure(figsize=(15,10))
corr=titanic_df.corr()
sns.heatmap(corr,annot=True,fmt="0.2f",cmap="coolwarm")

titanic_df.head()

# separate features & target variables
x=titanic_df.drop(axis=1,columns=['Survived'])
y=titanic_df['Survived']

"""# **8. Hyper Parameter tuning**"""

# import classification libraries
from sklearn.model_selection import RandomizedSearchCV,GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
import xgboost as xgb

# this code is to show how much time required to train the model using different algorithms
from datetime import datetime
def timer(start_time= None):
  if not start_time:
    start_time=datetime.now()
    return start_time
  elif start_time:
    thour,temp_sec=divmod((datetime.now()-start_time).total_seconds(),3600)
    tmin,tsec=divmod(temp_sec,60)
    print('\n Time taken: %i hours %i minutes and %s seconds. '% (thour,tmin,round(tsec,2)))

# parameters of all classification algorithms respectively
model_param={
    'random_forest':{
        'model':RandomForestClassifier(),
        'params':{
            'n_estimators':[1,5,10]
        }
    },
    'logistic_regression':{
        'model':LogisticRegression(multi_class='auto'),
        'params':{
            'C':[1,5,10]
        }
    },
    
    'decission_tree':{
        'model':DecisionTreeClassifier(),
        'params':{
            'criterion' : ["gini", "entropy"]
        }
    },
    'svm':{
        'model':SVC(gamma='auto'),
        'params':{
            'C':[1,10,20],
            'kernel':['rbf','linear']
        }
    },
    'xgboost':{
        'model':xgb.XGBClassifier(),
        'params':{
        'learning_rate':[0.20,0.30,0.35,0.37,0.40],
        'max_depth':[6,7,8,9,10],
        'min_child_weight':[5,7,8,9],
        'gamma':[0.0,0.1,0.2,0.3],
        'colsample_bytree':[0.5,0.7,0.8,0.9,1.0]
        }
    }
    
}

start_time=timer(None)
scores=[]
for model_name,mp in model_param.items():
    # Apply GridSearchCV
    rs=GridSearchCV(mp['model'],mp['params'],cv=5,return_train_score=False)
    rs.fit(x,y)
    scores.append({
        'model':model_name, # it'll retrive the best model name
        "best_score":rs.best_score_, # it'll retrive the best accuracy score
        'best_params':rs.best_params_ # it'll retrive the best parameter
    })
timer(start_time)

df=pd.DataFrame(scores,columns=['model','best_score','best_params'])
df

rs.best_params_

rs.best_estimator_

"""# **9.Model Building**


"""

# Apply KFold
from sklearn.model_selection import KFold
skf=KFold(n_splits=8)
xg3= xgb.XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1,
              colsample_bynode=1, colsample_bytree=0.7, gamma=0.2,
              learning_rate=0.37, max_delta_step=0, max_depth=7,
              min_child_weight=7, missing=None, n_estimators=100, n_jobs=1,
              nthread=None, objective='binary:logistic', random_state=0,
              reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=None,
              silent=None, subsample=1, verbosity=1)
for train_index,test_index in skf.split(x,y):
    x_train,x_test,y_train,y_test=x.loc[train_index],x.loc[test_index],y[train_index],y[test_index]
    xg3.fit(x_train, y_train)
xg3.score(x_train, y_train)

#Saving Scikitlearn models
import joblib
joblib.dump(xg3, "xgboost_titanic.pkl")

