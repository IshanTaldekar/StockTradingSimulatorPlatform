#!/bin/bash

if [ -d "package" ]; then
  rm -rf package
fi

if [ -f "news-summarizer-sagemaker-lambda-deployment-package.zip" ]; then
  rm news-summarizer-sagemaker-lambda-deployment-package.zip
fi

pip install -r requirements.txt -t ./package
cd package || exit
zip -r ../news-summarizer-sagemaker-lambda-deployment-package.zip .
cd ..
zip news-summarizer-sagemaker-lambda-deployment-package.zip news_summarizer_sagemaker_lambda.py