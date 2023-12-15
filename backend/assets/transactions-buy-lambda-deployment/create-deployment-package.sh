#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "transactions-buy-lambda-deployment-package.zip" ]; then
  rm transactions-buy-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../transactions-buy-lambda-deployment-package.zip .
cd ..
zip transactions-buy-lambda-deployment-package.zip transactions-buy-lambda.py