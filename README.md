# Project Documentation

## Overview

This project is a Dockerized application consisting of multiple services including a Flask web application, Celery workers, Redis, PostgreSQL, and Nginx. This guide provides instructions for managing the services, enabling and disabling maintenance mode, and updating the application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Starting the Application](#starting-the-application)
3. [Stopping the Application](#stopping-the-application)
4. [Enabling Maintenance Mode](#enabling-maintenance-mode)
5. [Disabling Maintenance Mode](#disabling-maintenance-mode)
6. [Updating the Code](#updating-the-code)
7. [Other Commands](#other-commands)

## Prerequisites

- Docker and Docker Compose installed on your system.
- Properly configured `.env` file in the root directory.

## Starting the Application

To start all services (including Nginx, Flask, Celery, Redis, and PostgreSQL), run:

```bash
docker-compose up -d
```

This command builds and starts the containers in detached mode.

## Stopping the Application

To stop all services (except Nginx), use:

```bash
docker-compose stop web celery_worker db redis
```

This will stop the specified services but keep Nginx running.

To stop all services including Nginx:

```bash
docker-compose down
```

## Enabling Maintenance Mode

To enable maintenance mode, follow these steps:

1. **Add Maintenance Page:**
   Create or copy the `maintenance.html` file to the Nginx HTML directory:

   ```bash
   cp ./docker/nginx/maintenance.html ./docker/nginx/html/
   ```

2. **Stop the Application Services:**
   Stop the application services while keeping Nginx running:

   ```bash
   docker-compose stop web celery_worker db redis
   ```

   The Nginx server will serve the maintenance page to users.

## Disabling Maintenance Mode

To disable maintenance mode, follow these steps:

1. **Remove Maintenance Page:**
   Remove the `maintenance.html` file from the Nginx HTML directory:

   ```bash
   rm ./docker/nginx/html/maintenance.html
   ```

2. **Restart the Application Services:**
   Start the application services again:

   ```bash
   docker-compose up -d
   ```

   This will bring up the services and Nginx will route traffic to your Flask application.

## Updating the Code

To update the application code:

1. **Pull Latest Changes:**
   If you are using version control (e.g., Git), pull the latest changes:

   ```bash
   git pull origin main
   ```

2. **Rebuild and Restart Containers:**
   Rebuild the Docker containers to include the updated code:

   ```bash
   docker-compose build
   docker-compose up -d
   ```

   This will ensure that your application is running the latest version of the code.

## Other Commands

- **View Logs for a Specific Service:**
  To view logs for a specific service, such as Flask:

  ```bash
  docker-compose logs -f web
  ```

- **Check Service Status:**
  To check the status of all services:

  ```bash
  docker-compose ps
  ```

- **Access a Service's Shell:**
  To access the shell of a running service, such as Flask:

  ```bash
  docker-compose exec web /bin/bash
  ```

## Notes

- Ensure that the paths to the Nginx configuration and maintenance page are correct.
- Make sure the `.env` file is properly configured with necessary environment variables.
