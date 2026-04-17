FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application
COPY . .

# Build for production
RUN npm run build

# Expose port
EXPOSE 3000

# Production mode
CMD ["npm", "start"]
