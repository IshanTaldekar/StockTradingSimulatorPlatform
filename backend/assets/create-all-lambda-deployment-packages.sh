#!/bin/bash

cd market-data-connect-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd market-data-disconnect-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd news-fetch-latest-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd news-search-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd news-summarizer-sagemaker-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd portfolio-fetch-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd transactions-buy-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd transactions-fetch-lambda-deployment || exit
sh create-deployment-package.sh
cd ..

cd transactions-sell-lambda-deployment || exit
sh create-deployment-package.sh
cd ..
