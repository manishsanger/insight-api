#!/bin/bash

# MongoDB initialization script
# This script runs when MongoDB container starts for the first time

echo "Initializing MongoDB with sample data..."

# Wait for MongoDB to be ready
sleep 10

# Create the database and collections
mongosh --username admin --password Apple@123 --authenticationDatabase admin <<EOF
use insight_db

// Create users collection with default admin
db.users.insertOne({
  username: "admin",
  password: "\$2b\$12\$LQv3c1yqBwEHxA1cyKm.DOEYdkTDmJWEGUQHWLAYeJq.qe9uF5HKy", // Apple@123
  role: "admin",
  created_at: new Date()
})

// Create default parameters
db.parameters.insertMany([
  {name: "person_name", description: "Name of the person involved", active: true},
  {name: "vehicle_number", description: "Vehicle license plate number", active: true},
  {name: "car_color", description: "Color of the vehicle", active: true},
  {name: "car_model", description: "Model of the vehicle", active: true},
  {name: "location", description: "Location where incident occurred", active: true},
  {name: "event_crime_violation", description: "Type of event, crime or violation", active: true}
])

echo "MongoDB initialization completed!"
EOF
