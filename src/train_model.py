from sklearn.linear_model import BayesianRidge
from sklearn.metrics import r2_score, root_mean_squared_error, mean_absolute_error
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np
from .targets import Targets
from .log import get_logger
import bentoml
import joblib

LOGGER = get_logger()

def load_data():
    X_train = pd.read_csv(Targets.processed('X_train.csv'))
    y_train = pd.read_csv(Targets.processed('y_train.csv'))
    X_test = pd.read_csv(Targets.processed('X_test.csv'))
    y_test = pd.read_csv(Targets.processed('y_test.csv'))
    return X_train, X_test, y_train, y_test

def normalize(X_train : pd.DataFrame, X_test : pd.DataFrame):
    scaler = MinMaxScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, Targets.processed('scaler.joblib'))
    return X_train_scaled, X_test_scaled

def train_model(X_train : np.array, y_train : pd.DataFrame):
    LOGGER.debug('Training linear model...')
    model = BayesianRidge()
    model.fit(X_train, y_train)
    LOGGER.info('Model trained.')
    return model

def test_model(model : BayesianRidge, X_test : np.array, y_test : pd.DataFrame):
    y_pred = model.predict(X_test)
    metrics = {
        'RMSE' : root_mean_squared_error(y_test, y_pred),
        'MAE' : mean_absolute_error(y_test, y_pred),
        'R2' : r2_score(y_test, y_pred)
    }
    LOGGER.info(f'Test done: {metrics=}')
    return metrics

def save_model(model : BayesianRidge):
    model_ref = bentoml.sklearn.save_model('admission_' + model.__class__.__name__.lower(), model)
    LOGGER.info(f'Model saved as: {model_ref}')
    
def main():
    X_train, X_test, y_train, y_test = load_data()
    X_train_scaled, X_test_scaled = normalize(X_train, X_test)
    model = train_model(X_train_scaled, y_train)
    test_model(model, X_test_scaled, y_test)
    save_model(model)


if __name__ == '__main__':
    main()

