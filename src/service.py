import bentoml
from pydantic import BaseModel
from typing import Literal
import numpy as np
from .log import get_logger
from .targets import Targets
import joblib
import jwt
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import uuid
import datetime

LOGGER = get_logger()

COLS = [
    'GRE Score',
    'TOEFL Score',
    'University Rating',
    'SOP',
    'LOR',
    'CGPA',
    'Research'
]

JWT_SECRET_KEY = 'ImustbeRANDOMuuid'
JWT_ALGORITHM = "HS256"

# User credentials for authentication
HARDCODED_USERS = {
    'guest' : 'ThePass123'
}

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path.startswith('/v1/models/admission/predict'):
            try:
                body = await request.json()
                token = body.get('token')
                if not token:
                    return JSONResponse(status_code=401, content={"detail": "Missing authentication token"})
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return JSONResponse(status_code=401, content={"detail": "Token has expired"})
            except jwt.InvalidTokenError:
                return JSONResponse(status_code=401, content={"detail": "Invalid token"})

            request.state.user = payload.get("sub")
        response = await call_next(request)
        return response

def create_jwt_token(user_id: str):
    expiration = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(hours=1)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

class Inputs(BaseModel):
    gre_score : int
    toefl_score : int
    university_rating : int
    sop : float
    lor : float
    cgpa : float
    research : Literal[0, 1]

class CredInputs(BaseModel):
    username : str
    password : str

@bentoml.service
class Predictor:
    def __init__(self):
        self.model = self.load_model()
        self.scaler = self.load_scaler()

    @bentoml.api(route='/login')
    def login(self, credentials: CredInputs) -> dict:
        username = credentials.username
        password = credentials.password
        if username in HARDCODED_USERS and HARDCODED_USERS[username] == password:
            token = create_jwt_token(username)
            return {'token': token}
        else:
            return JSONResponse(status_code=401, content={'detail': 'Invalid credentials'})

    @bentoml.api(route='/v1/models/admission/predict')
    async def predict(self, input : Inputs):
        input_arr = np.array([getattr(input, c.lower().replace(' ', '_')) for c in COLS]).reshape(1, -1)
        input_arr = self.scaler.transform(input_arr)
        result = self.model.predict(input_arr)
        return {'prediction' : result.tolist()}

    def load_model(self):
        # model = bentoml.sklearn.get('admission_bayesianridge:latest')
        model = bentoml.sklearn.load_model('admission_bayesianridge:latest')
        return model
    
    def load_scaler(self):
        scaler = joblib.load(Targets.processed('scaler.joblib'))
        return scaler

Predictor.add_asgi_middleware(JWTAuthMiddleware)