FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Create data directory
RUN mkdir -p /app/data

# Expose port
EXPOSE 8651

# Start the application
CMD ["npm", "start"]
