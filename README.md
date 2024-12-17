# Backend challenge: Cloud File Storage

## Service Goals
- [X] Users and authentication
- [X] Stats
- [X] Testing
- [X] Additional points:
    - Create a Docker image for running the API in a container
    - Swagger Documentation

## Usage
- Start the services: `docker compose up`
- Visit the FastAPI web [app](http://localhost:8000/docs) or the [Minio client](http://localhost:9001/)

## Testing
- With the services up enter into the fastapi service: `docker compose exec fastapi sh`
- Execute the tests (with coverage, in order to get a coverage report): `coverage run -m pytest app/testing.py`
- Print the report: `coverage report`