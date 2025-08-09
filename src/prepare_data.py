import pandas as pd
from sklearn.model_selection import train_test_split
from .targets import Targets
from .log import get_logger

TARGET = 'Chance of Admit'
DROPS = ['Serial No.']
LOGGER = get_logger()

def load_and_clean():
    df = pd.read_csv(Targets.raw('admission.csv'))
    df.columns = [c.strip() for c in df.columns]
    df.drop(columns=DROPS, inplace=True)
    df.dropna(inplace=True)
    return df

def split(df : pd.DataFrame):
    return train_test_split(df.drop(columns=[TARGET]), df[TARGET])

def save(df : pd.DataFrame, tag : str):
    target = Targets.processed(tag + '.csv')
    df.to_csv(target, index=False)
    LOGGER.debug(f'Save {tag} to {target}')

def main():
    df = load_and_clean()
    X_train, X_test, y_train, y_test = split(df)
    save(X_train, 'X_train')
    save(y_train, 'y_train')
    save(X_test, 'X_test')
    save(y_test, 'y_test')

if __name__ == '__main__':
    main()
