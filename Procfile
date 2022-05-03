#run: psql $DATABASE_URL --file="db/create.sql"
#run: npm install && npm run build
web: gunicorn --chdir ./api/src -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker wsgi:app
worker: celery --workdir ./api/src --app=cs.background.tasks.celery_app worker --concurrency=1
