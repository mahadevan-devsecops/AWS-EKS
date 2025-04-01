# Use a smaller base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only the requirements file first, so that the dependencies are cached unless requirements.txt changes
COPY requirements.txt .

# Install dependencies and clean up to reduce image size
RUN pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache

# Set environment variables for the database connection
#ENV DB_HOST=192.168.0.99
#ENV DB_USER=msuser
#ENV DB_PASSWORD=mspassword
#ENV DB_NAME=msdatabase

# Copy the rest of the application code
COPY app.py .

# Expose the necessary port
EXPOSE 80

# Run the application
CMD ["python", "app.py"]
