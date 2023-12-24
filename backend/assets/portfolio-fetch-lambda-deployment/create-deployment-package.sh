#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "portfolio-fetch-lambda-deployment-package.zip" ]; then
  rm portfolio-fetch-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../portfolio-fetch-lambda-deployment-package.zip .
cd ..
zip portfolio-fetch-lambda-deployment-package.zip portfolio_fetch_lambda.py
zip portfolio-fetch-lambda-deployment-package.zip user_portfolios_dao.py