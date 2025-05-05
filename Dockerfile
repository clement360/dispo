FROM node:23-slim

WORKDIR /usr/src/app

COPY package.json ./
RUN npm install

COPY src ./src
COPY .env.example ./ 
COPY systemd ./systemd
COPY scripts ./scripts

EXPOSE 80

CMD ["npm", "start"]

