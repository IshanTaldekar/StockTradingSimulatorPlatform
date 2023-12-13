import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Queue, QueueEncryption} from "aws-cdk-lib/aws-sqs";

export class SqsStack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        const marketDataUpdateQueue = new Queue(this, 'MarketDataUpdatesQueue', {
            queueName: 'market-data-update-queue',
            encryption: QueueEncryption.UNENCRYPTED,
        });

        const newsArticlesQueue = new Queue(this, 'NewsArticlesQueue', {
            queueName: 'news-articles-queue',
            encryption: QueueEncryption.UNENCRYPTED
        });
    }
}