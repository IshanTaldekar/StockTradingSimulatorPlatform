import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {AmazonLinuxImage, InstanceType, Vpc} from "aws-cdk-lib/aws-ec2";
import {AutoScalingGroup} from "aws-cdk-lib/aws-autoscaling";

export interface AutoScalingStackProps extends StackProps {
    readonly vpc: Vpc
}

export class AutoScalingStack extends Stack {
    constructor(scope: Construct, id: string, props: AutoScalingStackProps) {
        super(scope, id, props);

        const autoScalingGroup = new AutoScalingGroup(this, 'StockTradingPlatformASG', {
            vpc: props.vpc,
            instanceType: new InstanceType('t3.micro'),
            machineImage: new AmazonLinuxImage(),
            minCapacity: 2,
            maxCapacity: 5
        });

        autoScalingGroup.scaleOnRequestCount('ScalingPolicy', {
            targetRequestsPerMinute: 60
        });
    }
}