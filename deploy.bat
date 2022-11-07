sudo docker exec -d foodgram-project-react_web_1 python manage.py migrate
sudo docker exec -d foodgram-project-react_web_1 python manage.py collectstatic --no-input
sudo docker exec -d foodgram-project-react_web_1 python manage.py loaddata fixtures.json
sudo docker exec -d foodgram-project-react_web_1 cp -r static/. backend_static/
