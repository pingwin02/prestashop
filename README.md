# Prestashop project for Electronic Business

## LIST OF CONTENTS:

- [TECH-STACK](#tech-stack)
- [HOW TO UPLOAD/DOWNLOAD WEBSITE BACKUP](#how-to-uploaddownload-website-backup)
- [HOW TO RUN WEBSITE](#how-to-run-website)
- [HOW TO RUN API SCRIPT](#how-to-run-api-script)
- [ADMIN PANEL](#admin-panel)
- [RUN SCRAPER](#run-scraper)
- [RUN SELENIUM TESTS](#run-selenium-tests)
- [RUN SELENIUM TESTS](#run-selenium-tests)
- [AUTHORS](#authors)

## TECH-STACK:

1. Prestashop v1.7.8-apache
2. MariaDB
3. Docker
4. Python
5. Scrapy
6. Selenium
7. Google Drive API

## HOW TO UPLOAD/DOWNLOAD WEBSITE BACKUP:

1. Move to the `website` directory.

   ```
   cd website
   ```

2. Install virtual environment and packages.

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. To upload/download or delete backup use:

   ```
   python backup.py upload/download/delete
   ```

   To upload backup make sure that `mariadb` container is running.

4. Script will automatically create archive with backup and upload it to the Google Drive or download it and extract to the `website` directory.

## HOW TO RUN WEBSITE:

1. Install Docker.
2. Move to the `website` directory.

   ```
   cd website
   ```

3. Create and run containers using:

   ```
   docker compose up -d
   ```

4. Open your web browser and go to http://localhost:8080

5. To stop and remove containers use:

   ```
   docker compose down
   ```

## HOW TO RUN API SCRIPT

1. Move to the `api_service` directory.

   ```
   cd api_service
   ```

2. Install virtual environment and packages.

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run script using:

   ```
   python main.py
   ```

## ADMIN PANEL:

1. Open your web browser and go to http://localhost:8080/admin123

2. Login using:

   email:

   ```
   hermiona@ceo.com
   ```

   password:

   ```
   hermiona123!@#
   ```

## RUN SCRAPER:

1. Install Python on your machine.
2. Move to the `scraper` directory.

   ```
   cd scraper
   ```

3. Install virtual environment and packages.

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run scraper for categories and products.

   ```
   scrapy crawl categories
   scrapy crawl products
   ```

5. Results will be saved in `scraper_results` directory.

## RUN SELENIUM TESTS:

1. Install Python on your machine.
2. Move to the `selenium_tests` directory.

   ```
   cd selenium_tests
   ```

3. Install virtual environment and packages.

   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run tests.

   ```
   python main.py
   ```
   

## RUN SELENIUM TESTS:

1. Install Python on your machine.
2. Move to the `selenium_tests` directory.

   ```
   cd selenium_tests
   ```

3. Install chromedriver, virtual environment and packages.

   ```
   sudo apt install chromium-chromedriver
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run tests.

   ```
   python main.py
   ```

## AUTHORS:

- Maciej Szefler - 188614
- Damian Jankowski - 188597
- Kacper Karski - 186044
- Filp Krawczak - 191718
- Miraslau Farelnik - 191573
