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

export class StocksSimulatorStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const identityStack = new IdentityStack(this, 'IdentityStack', {
      env: env
    });

    const vpcStack = new VpcStack(this, 'VpcStack', {
      env: env
    });

    const autoScalingGroupStack = new AutoScalingGroupStack(this, 'AutoScalingGroupStack', {
      env: env,
      vpc: vpcStack.vpc,
      ec2ServerRole: identityStack.ec2ServerRole
    });
    autoScalingGroupStack.addDependency(vpcStack);
    autoScalingGroupStack.addDependency(identityStack);

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

    const openSearchServiceStack = new OpenSearchServiceStack(this, 'OpenSearchServiceStack', {
      env: env
    });
    openSearchServiceStack.addDependency(vpcStack);

    // TODO: needs Lambda deployments
    // const apiGatewayStack = new ApiGatewayStack(this, 'StockSimulatorAPIGatewayStack', {
    //
    // });
  }
}
