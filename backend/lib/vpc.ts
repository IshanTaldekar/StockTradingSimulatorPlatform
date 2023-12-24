import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {IpAddresses, Peer, Port, SecurityGroup, Vpc} from "aws-cdk-lib/aws-ec2";

export class VpcStack extends Stack {
    public readonly vpc;

    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        this.vpc = new Vpc(this, 'StockTradingPlatformVPC', {
            ipAddresses: IpAddresses.cidr('10.0.0.0/16')
        });
    }
}