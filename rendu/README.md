# Prerequisites
- docker
- python 3.11+
    - pytest (for testing only)
    - requests (for testing only)

Pip install prerequesites for testing:
```shell
pip install pytest requests
```
# Setup
Deploy archived docker image:
```shell
docker load -i bento_image.tar
```
# Usage
## Run Prediction Service
```shell
docker run --rm -p 3000:3000 poznyakov_predictor
```
## Test Prediction Service
```shell
pytest test.py
```
## Get Login Token Using Guest Credentials
```shell
curl -X 'POST' \
  'http://localhost:3000/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "credentials": {
    "username": "guest",
    "password": "ThePass123"
  }
}'
```
## Predict Admission From Shell
```shell
curl -X 'POST' \
  'http://localhost:3000/v1/models/admission/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "token" : "GeneratedToken",
  "input": {
    "gre_score": 337,
    "toefl_score": 118,
    "university_rating" : 2,
    "sop": 4.3,
    "lor": 4.4,
    "cgpa": 9.65,
    "research": 1
  }
}'
```

