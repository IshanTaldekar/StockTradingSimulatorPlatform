#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "transactions-sell-lambda-deployment-package.zip" ]; then
  rm transactions-sell-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../transactions-sell-lambda-deployment-package.zip .
cd ..
zip transactions-sell-lambda-deployment-package.zip transactions_sell_lambda.py
zip transactions-sell-lambda-deployment-package.zip user_portfolios_dao.py
zip transactions-sell-lambda-deployment-package.zip user_transactions_dao.py