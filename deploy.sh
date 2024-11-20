pip install -r requirements.txt          
python wbinsights/manage.py collectstatic --noinput
python wbinsights/manage.py makemigrations
python wbinsights/manage.py migrate
python wbinsights/manage.py compilemessages
#django-admin compilemessages
sudo service gunicorn restart