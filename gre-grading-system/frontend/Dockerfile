FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application
COPY . .

# Set API URL for build time (NEXT_PUBLIC_ vars are baked into JS at build)
ENV NEXT_PUBLIC_API_URL=https://gre-agent.onrender.com

# Build for production
RUN npm run build

# Expose port
EXPOSE 3000

# Production mode
CMD ["npm", "start"]
