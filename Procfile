run: psql $DATABASE_URL --file="db/create.sql"
web: gunicorn --chdir ./api/src -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker wsgi:app
