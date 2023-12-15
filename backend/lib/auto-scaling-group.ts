import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {AmazonLinuxImage, InstanceType, Vpc} from "aws-cdk-lib/aws-ec2";
import {AutoScalingGroup} from "aws-cdk-lib/aws-autoscaling";
import {Role} from "aws-cdk-lib/aws-iam";

export interface AutoScalingGroupStackProps extends StackProps {
    readonly vpc: Vpc,
    readonly ec2ServerRole: Role
}

export class AutoScalingGroupStack extends Stack {
    public readonly autoScalingGroup: AutoScalingGroup;

    constructor(scope: Construct, id: string, props: AutoScalingGroupStackProps) {
        super(scope, id, props);

        this.autoScalingGroup = new AutoScalingGroup(this, 'StockTradingPlatformASG', {
            vpc: props.vpc,
            instanceType: new InstanceType('t3.micro'),
            machineImage: new AmazonLinuxImage(),
            minCapacity: 2,
            maxCapacity: 5,
            role: props.ec2ServerRole
        });
    }
}