ARG NODE_VERSION='20.11.0'
ARG CYPRESS_VERSION='13.6.4'

FROM cypress/factory

COPY . /opt/app

WORKDIR /opt/app

RUN cypress cache prune

RUN npm install --save-dev cypress
