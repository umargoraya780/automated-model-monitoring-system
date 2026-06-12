# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the necessary project directories into the container
COPY serving/ /app/serving/
COPY model/ /app/model/

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the API using Uvicorn
CMD ["uvicorn", "serving.app:app", "--host", "0.0.0.0", "--port", "8000"]