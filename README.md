[![Deploy to server](https://github.com/se-pixs/backend/actions/workflows/deploy.yml/badge.svg)](https://github.com/se-pixs/backend/actions/workflows/deploy.yml)
[![Built with - Nextjs](https://img.shields.io/badge/Built_with-Django-214A23.svg?style=flat&logo=django)](https://www.djangoproject.com/)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ca43abfa3f7d45e28efdfce1b7dcc1fa)](https://www.codacy.com/gh/se-pixs/backend/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=se-pixs/backend&amp;utm_campaign=Badge_Grade)

# General
Frontend and backend are provisioned in seperate containers. However as we use serverside rendering, the conainers have to be connected to each other. Therfore each conainers should not be started stand alone through 
```docker run``` but by executing the corresponding docker-compose file, wich is located in the backend repository. This will provision both the backend and the frontend container and interconnect them as necessary.
The web application PiXS is then ready to use.

# Requirements
- Install docker
- Install docker-compose

# Getting started

- Clone the pixs/backend & pixs/frontend repositories
- Adjust settings to your environment
-- mv pixs.config.template.js pixs.config.js
       - In pixs/backend edit the Dockerfile
              -Set env BACKEND_RESOURCES_URL to 
              http://<IP of your host/FQDN of your host>:8000
              - Add hostname/FQDN to env ALLOWED_HOSTS
              Don't remove existing entrys
- Build the docker image for both repos
    ```shell
    cd /backend
    docker build . -t backend:latest
    cd ../frontend
    docker build . -t frontend:latest
    ```
- Provision frontend container (see frontend readme)
-   ```shell
    docker-compose up -d
    ```
