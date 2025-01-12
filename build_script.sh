#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Run database migrations
flask db upgrade

# Create uploads directory if it doesn't exist
mkdir -p uploads