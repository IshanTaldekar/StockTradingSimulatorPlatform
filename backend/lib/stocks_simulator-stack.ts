import { Construct } from 'constructs';
import {IdentityStack} from "./identity";
import {env} from "./config";
import {LoadBalancerStack} from "./load-balancer";
import {AutoScalingGroupStack} from "./auto-scaling-group";
import {VpcStack} from "./vpc";
import {CognitoStack} from "./cognito";
import {ApiGatewayStack} from "./api-gateway";
import {DynamoDBStack} from "./dynamo-db";
import {OpenSearchServiceStack} from "./opensearch-service";
import {Stack, StackProps} from "aws-cdk-lib";
import {Ec2Stack} from "./ec2";
import {LambdaStack} from "./lambda";
import {S3Stack} from "./s3";

export class StocksSimulatorStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const identityStack = new IdentityStack(this, 'IdentityStack', {
      env: env
    });

    const vpcStack = new VpcStack(this, 'VpcStack', {
      env: env
    });

    const s3Stack = new S3Stack(this, 'S3Stack', {
      env: env
    });

    const autoScalingGroupStack = new AutoScalingGroupStack(this, 'AutoScalingGroupStack', {
      env: env,
      vpc: vpcStack.vpc,
      ec2ServerRole: identityStack.ec2ServerRole
    });
    autoScalingGroupStack.addDependency(vpcStack);
    autoScalingGroupStack.addDependency(identityStack);
    autoScalingGroupStack.addDependency(s3Stack);

    const loadBalancerStack = new LoadBalancerStack(this, 'LoadBalancerStack', {
      env: env,
      vpc: vpcStack.vpc,
      autoScalingGroup: autoScalingGroupStack.autoScalingGroup
    });

    const cognitoStack = new CognitoStack(this, 'CognitoStack', {
      env: env,
      ec2ServerRole: identityStack.ec2ServerRole
    });

    const dynamoDBStack = new DynamoDBStack(this, 'DynamoDBStack', {
      env: env
    });

    // const ec2Stack = new Ec2Stack(this, 'EC2Stack', {
    //   env: env,
    //   vpc: vpcStack.vpc,
    //   ec2ServerRole: identityStack.ec2ServerRole
    // });
    // ec2Stack.addDependency(identityStack);

    const openSearchServiceStack = new OpenSearchServiceStack(this, 'OpenSearchServiceStack', {
      env: env
    });
    openSearchServiceStack.addDependency(vpcStack);

    const lambdaStack = new LambdaStack(this, 'LambdaStack', {
      env: env,
      marketDataConnectLambdaRole: identityStack.marketDataConnectLambdaRole,
      marketDataDisconnectLambdaRole: identityStack.marketDataDisconnectLambdaRole,
      transactionsFetchLambdaRole: identityStack.transactionsFetchLambdaRole,
      transactionsBuyLambdaRole: identityStack.transactionsBuyLambdaRole,
      transactionsSellLambdaRole: identityStack.transactionsSellLambdaRole,
      portfolioFetchLambdaRole: identityStack.portfolioFetchLambdaRole,
      newsFetchLatestAndSearchLambdaRole: identityStack.newsFetchLatestAndSearchLambdaRole,
      newsSummarizerLambdaRole: identityStack.newsSummarizerLambdaRole
    });
    lambdaStack.addDependency(identityStack);

    const apiGatewayStack = new ApiGatewayStack(this, 'StockSimulatorAPIGatewayStack', {
      env: env,
      marketDataConnectLambdaFunction: lambdaStack.marketDataConnectLambda,
      marketDataDisconnectLambdaFunction: lambdaStack.marketDataDisconnectLambda,
      transactionsFetchLambdaFunction: lambdaStack.transactionsFetchLambda,
      transactionsBuyLambdaFunction: lambdaStack.transactionsBuyLambda,
      transactionsSellLambdaFunction: lambdaStack.transactionsSellLambda,
      portfolioFetchLambdaFunction: lambdaStack.portfolioFetchLambda,
      newsFetchLatestLambdaFunction: lambdaStack.newsFetchLatestLambda,
      newsSearchLambdaFunction: lambdaStack.newsSearchLambda
    });
    apiGatewayStack.addDependency(lambdaStack);
  }
}
