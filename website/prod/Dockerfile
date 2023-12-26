FROM prestashop/prestashop:1.7.8-apache

COPY ./prestashop.crt /etc/ssl/certs/prestashop.crt
COPY ./prestashop.crt /usr/local/share/ca-certificates/prestashop.crt
COPY ./prestashop.key /etc/ssl/private/prestashop.key
COPY ./prestashop-ssl.conf /etc/apache2/sites-available/prestashop-ssl.conf

COPY ./src /var/www/html

WORKDIR /var/www/html

# remove cache under var/cache/prod and var/cache/dev
RUN rm -rf var/cache/* && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    chmod -R 777 var/cache var/logs

# remove install folder
RUN rm -rf install

RUN update-ca-certificates && a2enmod ssl && a2ensite prestashop-ssl
