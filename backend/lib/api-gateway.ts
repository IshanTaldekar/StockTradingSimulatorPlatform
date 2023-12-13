import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Cors, LambdaIntegration, Resource, RestApi} from "aws-cdk-lib/aws-apigateway";
import {IFunction} from "aws-cdk-lib/aws-lambda";

export interface APIGatewayStackProps extends StackProps {
    readonly marketDataConnectLambdaFunction: IFunction,
    readonly marketDataDisconnectLambdaFunction: IFunction,
    readonly transactionsFetchLambdaFunction: IFunction,
    readonly transactionsBuyLambdaFunction: IFunction,
    readonly transactionsSellLambdaFunction: IFunction,
    readonly newsFetchLatestLambdaFunction: IFunction,
    readonly newsSearchLambdaFunction: IFunction
}

export class ApiGatewayStack extends Stack {
    constructor(scope: Construct, id: string, props: APIGatewayStackProps) {
        super(scope, id, props);

        const capitalConnectApi = new RestApi(this, 'CapitalConnectAPI', {
            restApiName: 'capital-connect',
            defaultCorsPreflightOptions: {
                allowOrigins: Cors.ALL_ORIGINS,
                allowMethods: Cors.ALL_METHODS,
                allowHeaders: Cors.DEFAULT_HEADERS,
                allowCredentials: true
            }
        });

        const marketDataEndpoint = capitalConnectApi.root.addResource('market-data');
        const transactionsEndpoint = capitalConnectApi.root.addResource('transactions');
        const newsEndpoint = capitalConnectApi.root.addResource('news');

        this.createMarketDataAccessResources(marketDataEndpoint, props);
        this.createTransactionsAccessResources(transactionsEndpoint, props);
        this.createNewsAccessResources(newsEndpoint, props);
    }

    private createMarketDataAccessResources(marketDataResource: Resource, props: APIGatewayStackProps) {
        const connectResource = marketDataResource.addResource('connect');
        connectResource.addMethod('POST', new LambdaIntegration(props.marketDataConnectLambdaFunction));

        const disconnectResource = marketDataResource.addResource('disconnect');
        disconnectResource.addMethod('POST', new LambdaIntegration(props.marketDataDisconnectLambdaFunction));
    }

    private createTransactionsAccessResources(transactionsEndpoint: Resource, props: APIGatewayStackProps) {
        const transactionsFetchResource = transactionsEndpoint.addResource('fetch');
        transactionsFetchResource.addMethod('GET', new LambdaIntegration(props.transactionsFetchLambdaFunction));

        const transactionsBuyResource = transactionsEndpoint.addResource('buy');
        transactionsBuyResource.addMethod('POST', new LambdaIntegration(props.transactionsBuyLambdaFunction));

        const transactionsSellResource = transactionsEndpoint.addResource('sell');
        transactionsSellResource.addMethod('POST', new LambdaIntegration(props.transactionsSellLambdaFunction));
    }

    private createNewsAccessResources(newsEndpoint: Resource, props: APIGatewayStackProps) {
        const newsFetchResource = newsEndpoint.addResource('fetch-latest');
        newsFetchResource.addMethod('GET', new LambdaIntegration(props.newsFetchLatestLambdaFunction));

        const newsSearchResource = newsEndpoint.addResource('search');
        newsSearchResource.addMethod('GET', new LambdaIntegration(props.newsSearchLambdaFunction));
    }
}