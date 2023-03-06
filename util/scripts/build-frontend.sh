#!/bin/sh
#
# Script to build the web app front-end.
# Originally specified in the .gitlab-ci.yaml file

# Build a static production version of the webapp
cd device/webapp || exit
npm i
echo "API_URL=/" > .env
npm run build
