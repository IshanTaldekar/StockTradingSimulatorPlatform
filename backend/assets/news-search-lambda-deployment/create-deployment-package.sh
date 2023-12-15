#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "news-search-lambda-deployment-package.zip" ]; then
  rm news-search-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../news-search-lambda-deployment-package.zip .
cd ..
zip news-search-lambda-deployment-package.zip news-search-lambda.py