import {Stack, StackProps} from "aws-cdk-lib";
import {Port, SubnetType, Vpc} from "aws-cdk-lib/aws-ec2";
import {Construct} from "constructs";
import {AutoScalingGroup} from "aws-cdk-lib/aws-autoscaling";
import {ApplicationLoadBalancer} from "aws-cdk-lib/aws-elasticloadbalancingv2";

export interface LoadBalancerStackProps extends StackProps {
    readonly vpc: Vpc,
    readonly autoScalingGroup: AutoScalingGroup
}

export class LoadBalancerStack extends Stack {
    constructor(scope: Construct, id: string, props: LoadBalancerStackProps) {
        super(scope, id, props);

        const loadBalancer = new ApplicationLoadBalancer(this, 'StackTradingPlatformLoadBalancer', {
            vpc: props.vpc,
            vpcSubnets: {
                subnetType: SubnetType.PUBLIC
            },
            internetFacing: true,
        });

        const listener = loadBalancer.addListener('RequestsListener', {
            port: 80
        });

        listener.addTargets('RequestTargets', {
            port: 443,
            targets: [
                props.autoScalingGroup
            ]
        });

        loadBalancer.connections.allowFromAnyIpv4(Port.tcp(80));

        props.autoScalingGroup.scaleOnRequestCount('ScalingPolicy', {
            targetRequestsPerMinute: 60
        });
    }
}