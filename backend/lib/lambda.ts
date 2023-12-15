import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Code, Function, Runtime} from "aws-cdk-lib/aws-lambda";
import {Role} from "aws-cdk-lib/aws-iam";
import {RetentionDays} from "aws-cdk-lib/aws-logs";

export interface LambdaStackProps extends StackProps {
    readonly marketDataConnectLambdaRole: Role,
    readonly marketDataDisconnectLambdaRole: Role,
}

export class LambdaStack extends Stack {
    public readonly marketDataConnectLambda: Function;
    public readonly marketDataDisconnectLambda: Function;

    constructor(scope: Construct, id: string, props: LambdaStackProps) {
        super(scope, id, props);

        this.marketDataConnectLambda = new Function(this, 'MarketDataConnect', {
            functionName: 'market-data-connect',
            runtime: Runtime.PYTHON_3_10,
            handler: 'market-data-connect-lambda.handler',
            code: Code.fromAsset('backend/assets/market-data-connect-lambda-deployment/market-data-connect-lambda-deployment-package.zip'),
            role: props.marketDataConnectLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });

        this.marketDataDisconnectLambda = new Function(this, 'MarketDataDisconnect', {
            functionName: 'market-data-disconnect',
            runtime: Runtime.PYTHON_3_10,
            handler: 'market-data-disconnect-lambda.handler',
            code: Code.fromAsset('backend/assets/market-data-disconnect-lambda-deployment/market-data-disconnect-lambda-deployment-package.zip'),
            role: props.marketDataDisconnectLambdaRole,
            logRetention: RetentionDays.ONE_WEEK
        });
    }
}