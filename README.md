1. При установке на новый сервер необходимо установить зависимости
apt install build-essential libpq-dev python3-dev
чтобы установить psycopg2

2. При первой установке необходимо отключить метод start() в файле WebConfig 
чтобы не запускать scheduler, так как он запускается раньше чем созданы таблицы в БД

3. Необходимо установить gettext 
apt install gettext

4. Создаем папку для wbinsights/logs для хранения логов (в случае настройки handler: file)

5. Настройка systemctl сервиса
5.1. Создаем файл сокета
nano /etc/systemd/system/gunicorn.socket

с содержимым
[Unit]
Description=gunicorn socket

[Socket]
ListenStream=/run/gunicorn.sock

[Install]
WantedBy=sockets.target

5.2 Создаем файл сервиса
nano /etc/systemd/system/gunicorn.service

с содержимым
[Unit]
Description=gunicorn daemon
Requires=gunicorn.socket
After=network.target

[Service]
User=django
Group=django
WorkingDirectory=/app/wbinsights
#путь до каталога с файлом manage.py
ExecStart=/app/venv/bin/gunicorn \
        --workers 3 \
        --bind unix:/run/gunicorn.sock \
        wbinsights.wsgi:application


[Install]
WantedBy=multi-user.target

#путь до файла gunicorn в виртуальном окружении
/app/venv/bin/gunicorn 

5.3. 
Запускаем команды чтобы перезагрузить сервис
sudo systemctl daemon-reload
sudo systemctl start gunicorn.service
sudo systemctl status gunicorn.service
sudo systemctl enable gunicorn.service

6. в настройках nginx добавляем ограничениие по IP адресам(Yookassa) на доступ к URL подтверждения оплаты
location /appointment/payment/callback/ {

        allow 185.71.76.0/27;
        allow 185.71.77.0/27;
        allow 77.75.153.0/25;
        allow 77.75.156.11;
        allow 77.75.156.35;
        allow 77.75.154.128/25;
        allow 2a02:5180::/32;
        deny all;

        include proxy_params;
        proxy_pass http://unix:/run/gunicorn.sock;
}

7. В Yookassa меняем callback url, для отправки подтверждений об оплате

8. Устанавливаем certbot для управления SSL сертификатом let's encrypt
apt install certbot python3-certbot-nginx
certbot --nginx -d your_domain
systemctl restart nginx

9. Создать капчу v2 "я не робот" на сайте https://www.google.com/recaptcha/admin/
и поместить ключи в .env

10. Для того чтобы можно было перезагружать guniconr service не обладая root правами, 
необходимо выполнить следующие команды

в папке /etc/sudoers.d создаем файл, например, django-user-restart-gunicorn-service

с таким содержимым
#Allow django user restart gunicorn service
django ALL=(ALL) NOPASSWD: /usr/sbin/service gunicorn restart

далее сервис можно перезапускать командой
sudo service gunicorn restart