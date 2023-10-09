# Prestashop project for Electronic Business

## TECH-STACK:

1. Prestashop v1.7.8-apache
2. MariaDB
3. Docker

## HOW TO RUN WEBSITE:

1. Install Docker.
2. Move to the `website` directory.

   ```sh
   cd website
   ```

3. Create and run containers (`src` and `database` folders should appear)

   ```sh
   docker compose up -d
   ```

4. Open your web browser and go to http://localhost:8080

To stop and remove containers use:

```sh
docker compose down
```
