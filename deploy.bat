docker exec -d foodgram-project-react-web-1 python manage.py migrate
docker exec -d foodgram-project-react-web-1 python manage.py collectstatic --no-input
docker exec -d foodgram-project-react-web-1 python manage.py loaddata fixtures.json
docker exec -d foodgram-project-react-web-1 cp -r static/. backend_static/
