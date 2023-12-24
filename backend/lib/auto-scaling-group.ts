import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {
    AmazonLinuxImage,
    InstanceType,
    LaunchTemplate,
    MachineImage,
    OperatingSystemType, Peer, Port, SecurityGroup, SubnetType,
    UserData,
    Vpc
} from "aws-cdk-lib/aws-ec2";
import {AutoScalingGroup} from "aws-cdk-lib/aws-autoscaling";
import {Role} from "aws-cdk-lib/aws-iam";
import {readFileSync} from "fs";

export interface AutoScalingGroupStackProps extends StackProps {
    readonly vpc: Vpc,
    readonly ec2ServerRole: Role
}

export class AutoScalingGroupStack extends Stack {
    public readonly autoScalingGroup: AutoScalingGroup;

    constructor(scope: Construct, id: string, props: AutoScalingGroupStackProps) {
        super(scope, id, props);

        const startupSetupScript = readFileSync(
            'backend/assets/autoscaling-group-ec2-launch-config/ec2-launch-config.sh',
            'utf-8'
        );

        const userData = UserData.forLinux();
        userData.addCommands(startupSetupScript);

        const ec2ServerSecurityGroup = new SecurityGroup(this, 'AutoScalingGroupSecurityGroup', {
            vpc: props.vpc,
            allowAllOutbound: true
        });
        ec2ServerSecurityGroup.addIngressRule(Peer.anyIpv4(), Port.allTraffic());


        const launchTemplate = new LaunchTemplate(this, 'ServerLaunchTemplate', {
            userData: userData,
            instanceType: new InstanceType('t3.micro'),
            machineImage: MachineImage.fromSsmParameter(
                '/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id',
                {
                    os: OperatingSystemType.LINUX
                }
            ),
            role: props.ec2ServerRole,
            associatePublicIpAddress: true,
            keyName: 'ec2SshKey',
            securityGroup: ec2ServerSecurityGroup
        });

        this.autoScalingGroup = new AutoScalingGroup(this, 'StockTradingPlatformASG', {
            vpc: props.vpc,
            vpcSubnets: {
                subnetType: SubnetType.PUBLIC
            },
            minCapacity: 2,
            maxCapacity: 5,
            launchTemplate: launchTemplate
        });
    }
}