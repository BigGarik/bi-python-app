pip install -r requirements.txt          
python ./wbinsights/manage.py collectstatic --noinput
python ./wbinsights/manage.py migrate
service gunicorn restart