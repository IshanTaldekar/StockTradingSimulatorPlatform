import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {
    AmazonLinuxImage,
    Instance,
    InstanceType,
    MachineImage,
    OperatingSystemType,
    SubnetType,
    Vpc
} from "aws-cdk-lib/aws-ec2";
import {Role} from "aws-cdk-lib/aws-iam";

export interface Ec2StackProps extends StackProps {
    readonly vpc: Vpc,
    readonly ec2ServerRole: Role
}

export class Ec2Stack extends Stack {
    constructor(scope: Construct, id: string, props: Ec2StackProps) {
        super(scope, id, props);

        const instance = new Instance(this, 'frontend', {
            vpc: props.vpc,
            instanceType: new InstanceType('t3.micro'),
            machineImage: MachineImage.fromSsmParameter(
                '/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id',
                {
                    os: OperatingSystemType.LINUX
                }
            ),
            role: props.ec2ServerRole,
            allowAllOutbound: true,
            associatePublicIpAddress: true,
            keyName: 'palrsa',
            vpcSubnets: {
                subnetType: SubnetType.PUBLIC
            },
            sourceDestCheck: true
        });
    }
}