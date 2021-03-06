# import libraries
import re
import string
import pickle
import sys
import nltk
nltk.download(['punkt', 'wordnet'])

import numpy as np
import pandas as pd

import sqlite3
from sqlalchemy import create_engine


from sklearn.multioutput import MultiOutputClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV



def load_data(database_filepath):
    '''
    Input: 
        database_filepath (str): path to database file
    Output:
        X (pd.series): messages 
        Y (pd.dataFrame): sparse matrix of category relevance
        Y.columns (list): list of classes
    '''
    table_name = 'messages_disaster'
    engine = create_engine(f"sqlite:///{database_filepath}")
    df = pd.read_sql_query(f'SELECT * FROM {table_name}', engine)
    X = df[list(df.columns)[1]]
    Y = df[list(df.columns)[4:]]
    return X, Y, list(Y.columns)

def tokenize(text):
    '''
    Input:
        text (str): natural langueage text
    Output:
        clean_tokens (list): list of clean tokens
    '''
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")
    text.translate(str.maketrans('', '', string.punctuation))   
    tokens = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()

    clean_tokens = []
    for tok in tokens:
        clean_tok = lemmatizer.lemmatize(tok).lower().strip()
        clean_tokens.append(clean_tok)
        
    return clean_tokens


def build_model(grid_search=True):
    '''
    Input: 
        grid_search (bool): implement grid search
    Output:
        cv: Grid search with RandomForestClassifier
    '''
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(RandomForestClassifier()))
    ])
    if grid_search:
        parameters = {
            'vect__ngram_range': ((1, 1), (1, 2)),
            'vect__max_df': (0.5, 0.75, 1.0),
            'vect__max_features': (None, 5000, 10000),
            'tfidf__use_idf': (True, False),
            'clf__estimator__n_estimators': [50, 100, 200],
            'clf__estimator__min_samples_split': [2, 3, 4]
        }
        cv = GridSearchCV(pipeline, param_grid=parameters)
        return cv
    else:
        return pipeline
    


def evaluate_model(model, X_test, Y_test, category_names):
    '''
    Input:
        model: grid search model pipeline
        X_test (pd.dataFrame): disaster message test set 
        Y_test (pd.dataFrame): disaster category test set
    Output:
        None    
    '''
    Y_pred = model.predict(X_test)
    target_names = list(Y_test.columns)
    for i, col in enumerate(Y_test):
        print(f'{col} |------------------------------>')
        print(classification_report(Y_test[col], Y_pred[:,i], target_names=target_names))


def save_model(model, model_filepath):
    '''
    Input:
        model: Trained Model
        model_filepath (str): file path to save model
    Output:
        None
    '''
    pickle.dump(model, open(model_filepath, 'wb+'))

def main():
    if len(sys.argv) == 4:
        database_filepath, model_filepath, grid_serch = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, Y, category_names = load_data(database_filepath)
        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2)
        
        print('Building model...')
        # Grid search Consumes unreasionable resorce to compile on the project workspace         
        model = build_model(bool(grid_serch))
        
        print('Training model...')
        model.fit(X_train, Y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, Y_test, category_names)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()