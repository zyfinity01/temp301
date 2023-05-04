#!/bin/sh
#
# Performs user acceptance tests in CI pipeline.
# Originally specified in the .gitlab-ci.yaml file

# !!! Shellcheck raised a warning that this variable was referenced
# !!! but not assigned. It was not declared in .gitlab-ci.yaml and
# !!! there are no occurrences of this variable in the repository.
# !!! Set explicitly in this script and raise a warning.
azure_webapp_password=""
printf "WARNING: azure_webapp_password variable unset.\n"

# Build a static production version of the webapp
cd device/webapp || exit
npm i
echo "API_URL=/" >> .env
npm run build
# Copy built files to device simulator
cp -r build ../../device-simulator
cd ../../device-simulator || exit
mv build static
# copy device simulator configs
cp ../device/src/services/device-*.example.json .
# zip and deploy via curl
zip -r deploy.zip static/ webserver-simulator.py requirements.txt device-config.example.json device-data.example.json
echo "machine engr489-environmental-monitoring.scm.azurewebsites.net login engr489-azure-admin password $azure_webapp_password" > auth.txt
curl -X POST --netrc-file auth.txt --data-binary @"deploy.zip" https://engr489-environmental-monitoring.scm.azurewebsites.net/api/zipdeploy
