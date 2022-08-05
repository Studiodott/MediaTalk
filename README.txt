heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
heroku buildpacks:add heroku/nodejs
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
heroku config:set CONF_APP_SECRET="..."
heroku config:set CONF_DRIVE_FOLDER_ID="..."
heroku config:set CONF_DRIVE_API_KEY="..."
heroku config:set CONF_AWS_REGION="eu-central-1"
heroku config:set CONF_AWS_BUCKET="citystorytest"
heroku config:set AWS_SECRET_ACCESS_KEY="..."
heroku config:set AWS_ACCESS_KEY_ID="..."

