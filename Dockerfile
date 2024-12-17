# Use the official Python image with Alpine
FROM python:3.11-alpine

# Set the working directory inside the container
WORKDIR /src

# Copy the application code into the container
COPY ./requirements.txt /src/requirements.txt
COPY ./app /src/app
COPY ./.env /src/.env

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (adjust according to your FastAPI configuration, default FastAPI port is 8000)
EXPOSE 8000

# Run the FastAPI application
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]