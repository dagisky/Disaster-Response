import sys
import argparse
import os

def load_data(messages_filepath, categories_filepath):
    '''
    Input:
        messages_filepath (str): file path to messages dataset
        categories_filepath (str): file path to categories dataset
    Output:
        data (pd.dataFrame): merged dataset of messages and categories
    '''
    assert os.path.exists(messages_filepath) and os.path.exists(categories_filepath), '{} or {} dataset file not                  found!'.format(messages_filepath, categories_filepath)
    messages, categories = pd.read_csv(messages_filepath), pd.read_csv(categories_filepath)
    df = pd.merge(messages, categories, how='left', on=['id'])
    
    return df


def clean_data(df):
    '''
    Input:
        df (pandas.dataFrame): merged messages and categories data
    Output:
        df (pandas.dataFrame): Clean data
    '''
    categories = df['categories'].str.split(';', expand=True)
    # select the first row of the categories dataframe and extract a list of new column names for categories.
    category_colnames = categories.loc[0].apply(lambda x: str(x)[:-2])
    # rename the columns of `categories`
    categories.columns = category_colnames
    for column in categories:
        # set each value to be the last character of the string
        categories[column] = categories[column].str[-1]
        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
    # drop the original categories column from `df`
    df = df.drop(['categories'], axis=1)
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)
    # check for duplicates and drop
    if df.duplicated(subset=None, keep='first').sum():
        # drop duplicates
        df = df.drop_duplicates(keep='first', inplace=False)
        
    return df


def save_data(df, database_filename):
    pass  


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--task', default='18')#6
    parser.add_argument('--training', default=True)
    parser.add_argument('--dropout', default=0.1, type=float)
    parser.add_argument('--std-alpha', default=0.003, type=float)
    parser.add_argument('--test-split', default=0.1, type=float)
    parser.add_argument('--epoch', default=10000, type=int)
    parser.add_argument('--epoch_start', default=0, type=int)
    parser.add_argument('--exp-decay-rate', default=0.99, type=float)
    parser.add_argument('--use_cuda', default=True)
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()