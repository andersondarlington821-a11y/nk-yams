# ============================================================
#  NK's Yams — Dockerfile
#  Builds a lightweight Node.js 24 image
# ============================================================

FROM node:24-slim

# Set working directory inside container
WORKDIR /app

# Copy dependency files first (layer caching — faster rebuilds)
COPY package.json ./

# Install production dependencies only
RUN npm install --omit=dev

# Copy all application files
COPY . .

# Expose the API port
EXPOSE 5000

# Start the server
CMD ["node", "server.js"]
