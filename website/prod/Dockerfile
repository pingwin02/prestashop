FROM prestashop/prestashop:1.7.8-apache

COPY ./prestashop.crt /etc/ssl/certs/prestashop.crt
COPY ./prestashop.crt /usr/local/share/ca-certificates/prestashop.crt
COPY ./prestashop.key /etc/ssl/private/prestashop.key
COPY ./prestashop-ssl.conf /etc/apache2/sites-available/prestashop-ssl.conf
COPY ./init_script.sh /init_script.sh
COPY ./db_dump /db_dump

COPY ./src /var/www/html

COPY ./parameters.php /var/www/html/app/config/parameters.php

# remove cache under var/cache/prod and var/cache/dev
RUN rm -rf /var/www/html/var/cache/* && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    chmod -R 777 /var/www/html/var/cache /var/www/html/var/logs

# remove install folder
RUN rm -rf /var/www/html/install

RUN update-ca-certificates && a2enmod ssl && a2ensite prestashop-ssl
