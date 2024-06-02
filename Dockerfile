# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app
ENV PATH="/root/.local/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application code
COPY . /app/

# Expose the port the app runs on
EXPOSE 5000

# Initialize the database and create admin user
RUN pip install flask && \
    flask db init && \
    flask db migrate -m "Initial migration" && \
    flask db upgrade && \
    flask create_admin

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]
