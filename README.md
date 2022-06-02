# General
Frontend and backend are provisioned in seperate containers. However as we use serverside rendering, the conainers have to be connected to each other. Therfore each conainers should not be started stand alone through 
```docker run``` but by executing the corresponding docker-compose file, wich is located in the backend repository. This will provision both the backend and the frontend container and interconnect them as necessary.
The Webapplication PixS is then 

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
    docker build . -t $PWD:latest
    cd ../frontend
    docker build . -t $PWD:latest
    ```

- 
- provision frontend container (see frontend readme)
-   ```shell
    docker-compose up -d
    ```
