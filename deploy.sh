#!/bin/bash
set -x #echo on
sudo docker exec -d foodgram-project-react_web_1 python manage.py migrate
sleep 1
sudo docker exec -d foodgram-project-react_web_1 python manage.py collectstatic --no-input
sleep 1
sudo docker exec -d foodgram-project-react_web_1 python manage.py loaddata fixtures.json
sudo docker exec -d foodgram-project-react_web_1 cp -r static/. backend_static/
