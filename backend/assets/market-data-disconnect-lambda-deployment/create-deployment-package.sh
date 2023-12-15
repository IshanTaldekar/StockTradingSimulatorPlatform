#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "market-data-connect-lambda-deployment-package.zip" ]; then
  rm market-data-disconnect-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../market-data-disconnect-lambda-deployment-package.zip .
cd ..
zip market-data-disconnect-lambda-deployment-package.zip market-data-disconnect-lambda.py