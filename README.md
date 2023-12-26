# Prestashop project for Electronic Business

## LIST OF CONTENTS:

- [TECH-STACK](#tech-stack)
- [UPLOAD/DOWNLOAD WEBSITE BACKUP](#uploaddownload-website-backup)
- [RUN WEBSITE](#run-website)
- [RUN API SCRIPT](#run-api-script)
- [ADMIN PANEL](#admin-panel)
- [RUN SCRAPER](#run-scraper)
- [RUN SELENIUM TESTS](#run-selenium-tests)
- [RUN PRESTASHOP ON VPS SERVER](#run-prestashop-on-vps)
- [AUTHORS](#authors)

## TECH-STACK:

1. Prestashop v1.7.8-apache
2. MariaDB
3. Docker
4. Python
5. Scrapy
6. Selenium
7. Google Drive API

## UPLOAD/DOWNLOAD WEBSITE BACKUP:

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

## RUN WEBSITE:

1. Install Docker.
2. Move to the `website` directory.

   ```
   cd website
   ```

3. Generate ssl certificate using:

   ```
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout prestashop.key -out prestashop.crt -subj "/C=PL/ST=Greater Poland Voivodeship/L=Poznan/O=Komputerowe Imperium Hermiony/OU=Komputerowe Imperium Hermiony/CN=localhost"
   ```

4. Create and run containers using:

   ```
   docker compose up -d
   ```

5. Open your web browser and go to https://localhost

6. To stop and remove containers use:

   ```
   docker compose down
   ```

## RUN API SCRIPT

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

1. Open your web browser and go to https://localhost/admin123

2. Login using:

   email:

   ```
   prestashop@kursy.ct8.pl
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

## RUN PRESTASHOP ON VPS

1. Install OpenVPN on Windows or Tunnelblick on MacOS and configure VPN
   http://starter.eti.pg.gda.pl/openvpn/

2. Enable VPN and login to the broker server

   ```
   ssh rsww@172.20.83.101

   Password: qwe123
   ```

3. While on broker server, login to the destination server
   ```
   ssh hdoop@student-swarm01.maas

   Password: qwe123  
   ```

   You can provide any swarm server from swarm01 - swarm04

4. Go the the project destination:
   ```
   cd /opt/storage/actina15-20/block-storage/students/projects/studentsswarm-services/BE_186044
   ```

5. To deploy the app use:
   ```
   docker pull ryslek/be_186044_prestashop:latest
   docker stack deploy -c docker-compose.yml BE_186044 --with-registry-auth 
   ```

6. After deploying the app on any swarm claster, create proxy tunnel.

   6.1 Locate the node on which the app is served. It is under the 'node' section.
   ```
   docker service ps BE_186044
   ```
   6.2 Create tunnel. You need to do this on your local terminal. Try not to allocate typical ports to ABC as it may collapse with your default computer ports (like 80, 443, 22, 21 etc.):
   ```
   ssh -L ABC:student-swarm0S.maas:XYZ rsww@172.20.83.101
   ```

   Where:

      S - node where the app was deployed. It can be either 1, 2, 3 or 4

      ABC - port you want to listen on

      XYZ - port you want to forward your requests to
   
   Example:
   ```
   ssh -L 18604:student-swarm01.maas:18604 rsww@172.20.83.101
   ```

   6.3 On your browser, go to the localhost:ABC to see the app located on the swarm server on the port XYZ.

7. OPTIONAL - You can tunnel any service located on any swarm service. E.g. if you want to copy files from your computer to the swarm directory destination, create tunnel for typical SCP port (22).

   ```
   ssh -L 2222:student-swarm01.maas:22 rsww@172.20.83.101
   ```

   Than transfer any files you want:
   ```
   scp -r -P 2222 path/to/file/from hdoop@localhost:/opt/storage/actina15-20/block-storage/students/projects/students-swarm-services/BE_186044
   ```
8. While creating new docker image on public repository:

   8.1 Delete cache files
   ```
   sudo rm -rf src/var/cache/*    
   ```
   8.2 Modify database config in src/app/config/parameters.php
   ```
   'database_host' => 'student-swarm01.maas',
   'database_port' => '3306',
   'database_name' => 'BE_186044',
   'database_user' => 'root',
   'database_password' => 'student',
   ```

## AUTHORS:

- Maciej Szefler - 188614
- Damian Jankowski - 188597
- Kacper Karski - 186044
- Filp Krawczak - 191718
- Miraslau Farelnik - 191573
