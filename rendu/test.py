import datetime
import logging
import jwt
import requests

JWT_SECRET_KEY = 'ImustbeRANDOMuuid'
JWT_ALGORITHM = "HS256"

HARDCODED_USERS = {
    'guest' : 'ThePass123'
}

BAD_USERS = {
    'someuser' : 'asdfgz'
} 

PREDICTION_X = {
  "input": {
    "gre_score": 337,
    "toefl_score": 118,
    "university_rating": 4,
    "sop": 4.5,
    "lor": 4.5,
    "cgpa": 9.65,
    "research": 1
  }
}

PREDICTION_X_BAD = {
  "input": {
    "gre_score": 337,
    "toefl_score": 118,
    "sop": 4.5,
    "lor": 786,
    "cgpa": 9.65,
    "research": 1
  }
}


URL_LOGIN = "http://localhost:3000/login"
URL_PREDICT = "http://localhost:3000/v1/models/admission/predict"

def create_jwt_token(user_id: str, expired = False):
    expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1) if not expired else datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def test_auth_no_jwt():
    body = PREDICTION_X.copy()
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401
    body['token'] = 'badtoken'
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401
    
def test_auth_jwt_expired():
    body = PREDICTION_X.copy()
    body['token'] = create_jwt_token('guest',  True)
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401

def test_auth_jwt_ok():
    body = PREDICTION_X.copy()
    body['token'] = create_jwt_token('guest')
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 200

    
def test_api_login_ok():
    username, password = list(HARDCODED_USERS.items())[0]
    body = {
        'credentials' : {
            'username' : username,
            'password' : password
        }
    }
    result = requests.post(
        URL_LOGIN, 
        headers={"Content-Type": "application/json"},
        json=body)
    token = result.json().get('token')
    print(result.json())
    assert token is not None
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        assert False, "Token has expired"
    except jwt.InvalidTokenError:
        assert False, "Invalid token"
    else:
        assert True, "Valid token"

def test_api_login_fail():
    username, password = list(HARDCODED_USERS.items())[0]
    body = {
        'credentials' : {
            'username' : username,
            'password' : 'bad'
        }
    }
    result = requests.post(
        URL_LOGIN, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401

def test_api_no_jwt():
    body = PREDICTION_X.copy()
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401
    body['token'] = 'badtoken'
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 401

def test_api_pred_ok():
    body = PREDICTION_X.copy()
    body['token'] = create_jwt_token('guest')
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 200
    assert isinstance(result.json().get('prediction', ['failed'])[0], float)

def test_api_pred_bad():
    body = PREDICTION_X_BAD.copy()
    body['token'] = create_jwt_token('guest')
    result = requests.post(
        URL_PREDICT, 
        headers={"Content-Type": "application/json"},
        json=body)
    assert result.status_code == 400

