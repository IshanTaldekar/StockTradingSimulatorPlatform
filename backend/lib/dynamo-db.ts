import {RemovalPolicy, Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {AttributeType, TableClass, TableV2} from "aws-cdk-lib/aws-dynamodb";

export class DynamoDBStack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        const connectedSocketsTable = new TableV2(this, 'ConnectedSocketsTable', {
            tableName: 'market-data-connections',
            partitionKey: {
                name: 'connection-id',
                type: AttributeType.STRING
            },
            tableClass: TableClass.STANDARD_INFREQUENT_ACCESS,
            removalPolicy: RemovalPolicy.DESTROY
        });

        const userTransactionsTable = new TableV2(this, 'UserTransactionsTable', {
            tableName: 'user-transactions',
            partitionKey: {
                name: 'key',
                type: AttributeType.STRING
            },
            tableClass: TableClass.STANDARD_INFREQUENT_ACCESS,
            removalPolicy: RemovalPolicy.DESTROY
        });

        const userPotfolioTable = new TableV2(this, 'UserPortfolioTable', {
            tableName: 'user-portfolios',
            partitionKey: {
                name: 'key',
                type: AttributeType.STRING
            },
            tableClass: TableClass.STANDARD_INFREQUENT_ACCESS,
            removalPolicy: RemovalPolicy.DESTROY
        })
    }
}