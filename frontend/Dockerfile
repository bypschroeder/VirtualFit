FROM node:22.12.0

WORKDIR /frontend

RUN apt-get update

COPY . /frontend/
RUN npm install

EXPOSE 5173

ENTRYPOINT [ "npm", "run", "dev" ]
