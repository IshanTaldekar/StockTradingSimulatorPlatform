import {Arn, ArnFormat, Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Effect, PolicyDocument, PolicyStatement, Role, ServicePrincipal} from "aws-cdk-lib/aws-iam";

export class IdentityStack extends Stack {
    public readonly ec2ServerRole: Role;
    public readonly marketDataConnectLambdaRole: Role;
    public readonly marketDataDisconnectLambdaRole: Role;
    public readonly transactionsFetchLambdaRole: Role;
    public readonly transactionsBuyLambdaRole: Role;
    public readonly transactionsSellLambdaRole: Role;
    public readonly portfolioFetchLambdaRole: Role;
    public readonly newsFetchLatestAndSearchLambdaRole: Role;

    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        this.ec2ServerRole = new Role(this, 'EC2ServerRole', {
            assumedBy: new ServicePrincipal('ec2.amazonaws.com')
        });

        // TODO: add market data timestream access
        this.marketDataConnectLambdaRole = new Role(this, 'MarketDataConnectLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                MarketDataConnectionsDynamoDBAccess: this.getMarketDataConnectionsDynamoDBAccessPolicy(),
            }
        });

        this.marketDataDisconnectLambdaRole = new Role(this, 'MarketDataDisconnectLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                MarketDataConnectionsDynamoDBAccess: this.getMarketDataConnectionsDynamoDBAccessPolicy()
            }
        });

        this.transactionsFetchLambdaRole = new Role(this, 'TransactionsFetchLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                UserTransactionsDynamoDBAccess: this.getUserTransactionsDynamoDBAccessPolicy()
            }
        });

        this.transactionsBuyLambdaRole = new Role(this, 'TransactionsBuyLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                UserTransactionsDynamoDBAccess: this.getUserTransactionsDynamoDBAccessPolicy(),
                UserPortfoliosDynamoDBAccess: this.getUserPortfoliosDynamoDBAccessPolicy()
            }
        });

        this.transactionsSellLambdaRole = new Role(this, 'TransactionsSellLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                UserTransactionsDynamoDBAccess: this.getUserTransactionsDynamoDBAccessPolicy(),
                UserPortfoliosDynamoDBAccess: this.getUserPortfoliosDynamoDBAccessPolicy()
            }
        });

        this.portfolioFetchLambdaRole = new Role(this, 'PortfolioFetchLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                UserPortfoliosDynamoDBAccess: this.getUserPortfoliosDynamoDBAccessPolicy()
            }
        });

        this.newsFetchLatestAndSearchLambdaRole = new Role(this, 'NewsFetchLatestLambdaRole', {
            assumedBy: new ServicePrincipal('lambda.amazonaws.com'),
            inlinePolicies: {
                CloudWatchLogsAccess: this.getCloudWatchLogsAccessPolicy(),
                OpenSearchAccess: this.getOpensearchServiceAccessPolicy()
            }
        });
    }

    private getCloudWatchLogsAccessPolicy(): PolicyDocument {
        return new PolicyDocument({
            statements: [
                new PolicyStatement({
                    actions: [
                        'logs:CreateLogGroup',
                        'logs:CreateLogStream',
                        'logs:PutLogEvents'
                    ],
                    effect: Effect.ALLOW,
                    resources: ['*']
                })
            ]
        });
    }

    private getMarketDataConnectionsDynamoDBAccessPolicy(): PolicyDocument {
        return new PolicyDocument({
            statements: [
                new PolicyStatement({
                    actions: [
                        'dynamodb:GetItem',
                        'dynamodb:Query',
                        'dynamodb:PutItem',
                        'dynamodb:Scan',
                        'dynamodb:UpdateItem',
                        'dynamodb:DeleteItem'
                    ],
                    effect: Effect.ALLOW,
                    resources: [
                        Arn.format(
                            {
                                arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                service: 'dynamodb',
                                resource: 'table',
                                resourceName: 'market-data-connections'
                            },
                            this
                        )
                    ]
                })
            ]
        });
    }

    private getUserTransactionsDynamoDBAccessPolicy(): PolicyDocument {
        return new PolicyDocument({
            statements: [
                new PolicyStatement({
                    actions: [
                        'dynamodb:GetItem',
                        'dynamodb:Query',
                        'dynamodb:PutItem',
                        'dynamodb:Scan',
                        'dynamodb:UpdateItem',
                        'dynamodb:DeleteItem'
                    ],
                    effect: Effect.ALLOW,
                    resources: [
                        Arn.format(
                            {
                                arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                service: 'dynamodb',
                                resource: 'table',
                                resourceName: 'user-transactions'
                            },
                            this
                        )
                    ]
                })
            ]
        });
    }

    private getUserPortfoliosDynamoDBAccessPolicy(): PolicyDocument {
        return new PolicyDocument({
            statements: [
                new PolicyStatement({
                    actions: [
                        'dynamodb:GetItem',
                        'dynamodb:Query',
                        'dynamodb:PutItem',
                        'dynamodb:Scan',
                        'dynamodb:UpdateItem',
                        'dynamodb:DeleteItem'
                    ],
                    effect: Effect.ALLOW,
                    resources: [
                        Arn.format(
                            {
                                arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                service: 'dynamodb',
                                resource: 'table',
                                resourceName: 'user-portfolios'
                            },
                            this
                        )
                    ]
                })
            ]
        });
    }

    private getOpensearchServiceAccessPolicy(): PolicyDocument {
        return new PolicyDocument({
            statements: [
                new PolicyStatement({
                    actions: [
                        'es:ESHttpGet',
                        'es:ESHttpPut'
                    ],
                    effect: Effect.ALLOW,
                    resources: [
                        Arn.format(
                            {
                                arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                service: 'es',
                                resource: 'domain',
                                resourceName: 'news-summary/*',
                            },
                            this
                        )
                    ]
                })
            ]
        });
    }
}