#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "transactions-fetch-lambda-deployment-package.zip" ]; then
  rm transactions-fetch-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../transactions-fetch-lambda-deployment-package.zip .
cd ..
zip transactions-fetch-lambda-deployment-package.zip transactions_fetch_lambda.py