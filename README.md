# Prestashop project for Electronic Business

## TECH-STACK:

1. Python
2. Scrapy

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
