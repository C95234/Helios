# Build : compile les sources React/Vite en fichiers statiques.
FROM node:20-slim AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# VITE_API_BASE_URL est lu au moment du build par Vite (variable d'environnement
# cote build, pas cote runtime -- a fournir via --build-arg si le backend est
# sur un domaine different du frontend).
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

# Serve : nginx sert les fichiers statiques et gere le routage SPA.
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
