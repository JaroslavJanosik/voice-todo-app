FROM node:24-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run prepare
RUN npm run build

FROM node:24-alpine

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=4173

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts \
    && adduser -D -u 10001 appuser \
    && npm cache clean --force

COPY --from=build /app/build ./build

EXPOSE 4173

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=5 CMD node -e "fetch('http://127.0.0.1:4173/').then((response) => process.exit(response.ok ? 0 : 1)).catch(() => process.exit(1))"

CMD ["node", "build"]
