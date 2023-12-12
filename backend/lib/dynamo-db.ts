import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {AttributeType, TableClass, TableV2} from "aws-cdk-lib/aws-dynamodb";

export class DynamoDBStack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        const connectedSocketsTable = new TableV2(this, 'ConnectedSocketsTable', {
            tableName: 'connected-sockets',
            partitionKey: {
                name: 'key',
                type: AttributeType.STRING
            },
            tableClass: TableClass.STANDARD_INFREQUENT_ACCESS,
        });

        const userTransactionsTable = new TableV2(this, 'UserTransactionsTable', {
            tableName: 'user-transactions',
            partitionKey: {
                name: 'key',
                type: AttributeType.STRING
            },
            tableClass: TableClass.STANDARD_INFREQUENT_ACCESS
        });
    }
}