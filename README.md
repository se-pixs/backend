[![Deploy to server](https://github.com/se-pixs/backend/actions/workflows/deploy.yml/badge.svg)](https://github.com/se-pixs/backend/actions/workflows/deploy.yml)
[![Built with - Nextjs](https://img.shields.io/badge/Built_with-Django-214A23.svg?style=flat&logo=django)](https://www.djangoproject.com/)

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/ca43abfa3f7d45e28efdfce1b7dcc1fa)](https://www.codacy.com/gh/se-pixs/backend/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=se-pixs/backend&amp;utm_campaign=Badge_Grade)

# General
Frontend and backend are provisioned in seperate containers. However as we use serverside rendering, the conainers have to be connected to each other. Therfore each conainers should not be started stand alone through 
```docker run``` but by executing the corresponding docker-compose file, wich is located in the backend repository. This will provision both the backend and the frontend container and interconnect them as necessary.
The Webapplication PixS is then 

# Requirements
- Install docker
- Install docker-compose

# Getting started

- First clone the backend Repository
-   ```shell
    cd /backend
    ```

-   ```shell
    docker build . -t backend:latest
    ```
- provision frontend container (see frontend readme)
-   ```shell
    docker-compose up -d
    ```
