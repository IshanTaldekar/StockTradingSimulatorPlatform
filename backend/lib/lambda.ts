import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Code, Function, Runtime} from "aws-cdk-lib/aws-lambda";
import {Role} from "aws-cdk-lib/aws-iam";
import {RetentionDays} from "aws-cdk-lib/aws-logs";

export interface LambdaStackProps extends StackProps {
    readonly marketDataConnectLambdaRole: Role,
    readonly marketDataDisconnectLambdaRole: Role,
    readonly transactionsFetchLambdaRole: Role,
    readonly transactionsBuyLambdaRole: Role,
    readonly transactionsSellLambdaRole: Role,
    readonly portfolioFetchLambdaRole: Role,
    readonly newsFetchLatestAndSearchLambdaRole: Role,
}

export class LambdaStack extends Stack {
    public readonly marketDataConnectLambda: Function;
    public readonly marketDataDisconnectLambda: Function;
    public readonly transactionsFetchLambda: Function;
    public readonly transactionsBuyLambda: Function;
    public readonly transactionsSellLambda: Function;
    public readonly portfolioFetchLambda: Function;
    public readonly newsFetchLatestLambda: Function;
    public readonly newsSearchLambda: Function;

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        this.marketDataConnectLambda = new Function(this, 'MarketDataConnect', {
            functionName: 'market-data-connect',
            runtime: Runtime.PYTHON_3_10,
            handler: 'market_data_connect_lambda.handler',
            code: Code.fromAsset('backend/assets/market-data-connect-lambda-deployment/market-data-connect-lambda-deployment-package.zip'),
            role: props.marketDataConnectLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.marketDataDisconnectLambda = new Function(this, 'MarketDataDisconnect', {
            functionName: 'market-data-disconnect',
            runtime: Runtime.PYTHON_3_10,
            handler: 'market_data_disconnect_lambda.handler',
            code: Code.fromAsset('backend/assets/market-data-disconnect-lambda-deployment/market-data-disconnect-lambda-deployment-package.zip'),
            role: props.marketDataDisconnectLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.transactionsFetchLambda = new Function(this, 'TransactionsFetch', {
            functionName: 'transactions-fetch',
            runtime: Runtime.PYTHON_3_10,
            handler: 'transactions_fetch_lambda.handler',
            code: Code.fromAsset('backend/assets/transactions-fetch-lambda-deployment/transactions-fetch-lambda-deployment-package.zip'),
            role: props.transactionsFetchLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.transactionsBuyLambda = new Function(this, 'TransactionsBuy', {
            functionName: 'transactions-buy',
            runtime: Runtime.PYTHON_3_10,
            handler: 'transactions_buy_lambda.handler',
            code: Code.fromAsset('backend/assets/transactions-buy-lambda-deployment/transactions-buy-lambda-deployment-package.zip'),
            role: props.transactionsBuyLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.transactionsSellLambda = new Function(this, 'TransactionsSell', {
            functionName: 'transactions-sell',
            runtime: Runtime.PYTHON_3_10,
            handler: 'transactions_sell_lambda.handler',
            code: Code.fromAsset('backend/assets/transactions-sell-lambda-deployment/transactions-sell-lambda-deployment-package.zip'),
            role: props.transactionsSellLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.portfolioFetchLambda = new Function(this, 'PortfolioFetch', {
            functionName: 'portfolio-fetch',
            runtime: Runtime.PYTHON_3_10,
            handler: 'portfolio_fetch_lambda.handler',
            code: Code.fromAsset('backend/assets/portfolio-fetch-lambda-deployment/portfolio-fetch-lambda-deployment-package.zip'),
            role: props.portfolioFetchLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.newsFetchLatestLambda = new Function(this, 'NewsFetchLatest', {
            functionName: 'news-fetch-latest',
            runtime: Runtime.PYTHON_3_10,
            handler: 'news_fetch_latest_lambda.handler',
            code: Code.fromAsset('backend/assets/news-fetch-latest-lambda-deployment/news-fetch-latest-lambda-deployment-package.zip'),
            role: props.newsFetchLatestAndSearchLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.newsSearchLambda = new Function(this, 'NewsSearchLatest', {
            functionName: 'news-search',
            runtime: Runtime.PYTHON_3_10,
            handler: 'news_search_lambda.handler',
            code: Code.fromAsset('backend/assets/news-search-lambda-deployment/news-search-lambda-deployment-package.zip'),
            role: props.newsFetchLatestAndSearchLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });
    }
}