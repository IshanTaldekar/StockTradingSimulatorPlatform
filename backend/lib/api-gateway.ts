import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Cors, LambdaIntegration, Resource, RestApi} from "aws-cdk-lib/aws-apigateway";
import {IFunction} from "aws-cdk-lib/aws-lambda";
import {WebSocketApi} from "aws-cdk-lib/aws-apigatewayv2";
import {WebSocketLambdaIntegration} from "aws-cdk-lib/aws-apigatewayv2-integrations";

export interface APIGatewayStackProps extends StackProps {
    readonly marketDataConnectLambdaFunction: IFunction,
    readonly marketDataDisconnectLambdaFunction: IFunction,
    readonly transactionsFetchLambdaFunction: IFunction,
    readonly transactionsBuyLambdaFunction: IFunction,
    readonly transactionsSellLambdaFunction: IFunction,
    readonly portfolioFetchLambdaFunction: IFunction,
    readonly newsFetchLatestLambdaFunction: IFunction,
    readonly newsSearchLambdaFunction: IFunction
}

export class ApiGatewayStack extends Stack {
    constructor(scope: Construct, id: string, props: APIGatewayStackProps) {
        super(scope, id, props);

        const capitalConnectApi = new WebSocketApi(this, 'CapitalConnectAPI', {
            apiName: 'capital-connect',
            connectRouteOptions: {
                integration: new WebSocketLambdaIntegration('ConnectIntegration', props.marketDataConnectLambdaFunction),
                returnResponse: true
            },
            disconnectRouteOptions: {
                integration: new WebSocketLambdaIntegration('DisconnectIntegration', props.marketDataDisconnectLambdaFunction)
            }
        });

        const investorCompanionApi = new RestApi(this, 'InvestorCompanionAPI', {
            restApiName: 'investor-companion',
            defaultCorsPreflightOptions: {
                allowOrigins: Cors.ALL_ORIGINS,
                allowMethods: Cors.ALL_METHODS,
                allowHeaders: Cors.DEFAULT_HEADERS,
                allowCredentials: true
            },
            retainDeployments: false
        });
        const transactionsEndpoint = investorCompanionApi.root.addResource('transactions');
        const portfolioEndpoint = investorCompanionApi.root.addResource('portfolio');
        const newsEndpoint = investorCompanionApi.root.addResource('news');

        this.createTransactionsAccessResources(transactionsEndpoint, props);
        this.createPortfolioAccessResources(portfolioEndpoint, props);
        this.createNewsAccessResources(newsEndpoint, props);
    }

    private createTransactionsAccessResources(transactionsEndpoint: Resource, props: APIGatewayStackProps) {
        const transactionsFetchResource = transactionsEndpoint.addResource('fetch');
        const transactionsFetchUsernameResource = transactionsFetchResource.addResource('{username}');
        transactionsFetchUsernameResource.addMethod('GET', new LambdaIntegration(props.transactionsFetchLambdaFunction));

        const transactionsBuyResource = transactionsEndpoint.addResource('buy');
        transactionsBuyResource.addMethod('POST', new LambdaIntegration(props.transactionsBuyLambdaFunction));

        const transactionsSellResource = transactionsEndpoint.addResource('sell');
        transactionsSellResource.addMethod('POST', new LambdaIntegration(props.transactionsSellLambdaFunction));
    }

    private createPortfolioAccessResources(portfolioEndpoint: Resource, props: APIGatewayStackProps) {
        const portfolioFetchResource = portfolioEndpoint.addResource('fetch');
<<<<<<< HEAD
        portfolioFetchResource.addMethod('GET', new LambdaIntegration(props.portfolioFetchLambdaFunction));
=======
        const portfolioFetchUsernameResource = portfolioFetchResource.addResource('{user}');
        portfolioFetchUsernameResource.addMethod('GET', new LambdaIntegration(props.portfolioFetchLambdaFunction));
>>>>>>> 37d6d69 (build: add infrastructure deployments)
    }

    private createNewsAccessResources(newsEndpoint: Resource, props: APIGatewayStackProps) {
        const newsFetchResource = newsEndpoint.addResource('fetch-latest');
        newsFetchResource.addMethod('GET', new LambdaIntegration(props.newsFetchLatestLambdaFunction));

        const newsSearchResource = newsEndpoint.addResource('search');
        const newsSearchKeywordResource = newsSearchResource.addResource('{keyword}');
        newsSearchKeywordResource.addMethod('GET', new LambdaIntegration(props.newsSearchLambdaFunction));
    }
}