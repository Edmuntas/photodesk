FROM node:22-alpine

WORKDIR /app

# Install backend dependencies
COPY apps/backend/package*.json ./apps/backend/
RUN cd apps/backend && npm ci --only=production

# Copy application code
COPY apps/backend/ ./apps/backend/
COPY apps/frontend/declutter.html ./apps/frontend/
COPY core/ai/prompts.json ./core/ai/
COPY core/ai/grok_models.json ./core/ai/

# Create data directories
RUN mkdir -p data/results data/uploads

# Environment
ENV NODE_ENV=production
ENV PORT=3001
ENV RESULTS_DIR=/app/data/results
ENV UPLOADS_DIR=/app/data/uploads

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget -qO- http://localhost:3001/api/sessions || exit 1

CMD ["node", "apps/backend/server.js"]
