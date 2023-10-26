# Prestashop project for Electronic Business

## TECH-STACK:

1. Prestashop v1.7.8-apache
2. MariaDB
3. Docker
4. Python
5. Scrapy

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

## RUN SCRAPER:

1. Install Python on your machine.
2. Move to the `scraper` directory.

   ```sh
   cd scraper
   ```

3. Install virtual environment and packages.

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run scraper for categories and products.

   ```sh
   scrapy crawl categories
   scrapy crawl products
   ```

5. Results will be saved in `scraper` directory.

## AUTHORS:

- Maciej Szefler - 188614
- Damian Jankowski - 188597
- Kacper Karski - 186044
- Filp Krawczak - 191718
- Miraslau Farelnik - 191573
