import * as cdk from 'aws-cdk-lib';
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

export class StocksSimulatorStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const identityStack = new IdentityStack(this, 'StocksSimulatorIdentityStack', {
      env: env
    });

    const vpcStack = new VpcStack(this, 'StockSimulatorVpcStack', {
      env: env
    });

    const autoScalingGroupStack = new AutoScalingGroupStack(this, 'StocksSimulatorAutoScalingGroupStack', {
      env: env,
      vpc: vpcStack.vpc,
      ec2ServerRole: identityStack.ec2ServerRole
    });
    autoScalingGroupStack.addDependency(vpcStack);
    autoScalingGroupStack.addDependency(identityStack);

    const loadBalancerStack = new LoadBalancerStack(this, 'StocksSimulatorLoadBalancerStack', {
      env: env,
      vpc: vpcStack.vpc,
      autoScalingGroup: autoScalingGroupStack.autoScalingGroup
    });
    loadBalancerStack.addDependency(autoScalingGroupStack);

    const cognitoStack = new CognitoStack(this, 'StocksSimulatorCognitoStack', {
      env: env,
      ec2ServerRole: identityStack.ec2ServerRole
    });
    cognitoStack.addDependency(identityStack);

    const dynamoDBStack = new DynamoDBStack(this, 'StocksSimulatorDynamoDBStack', {
      env: env
    });

    const openSearchServiceStack = new OpenSearchServiceStack(this, 'StocksSimulatorOpenSearchServiceStack', {
      vpc: vpcStack.vpc
    });
    openSearchServiceStack.addDependency(vpcStack);

    // TODO: needs Lambda deployments
    // const apiGatewayStack = new ApiGatewayStack(this, 'StockSimulatorAPIGatewayStack', {
    //
    // });
  }
}
