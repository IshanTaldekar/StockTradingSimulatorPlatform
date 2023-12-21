#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "news-fetch-latest-lambda-deployment-package.zip" ]; then
  rm news-fetch-latest-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../news-fetch-latest-lambda-deployment-package.zip .
cd ..
zip news-fetch-latest-lambda-deployment-package.zip news_fetch_latest_lambda.py