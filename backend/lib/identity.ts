import {Arn, Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Effect, PolicyDocument, PolicyStatement, Role, ServicePrincipal} from "aws-cdk-lib/aws-iam";

export class IdentityStack extends Stack {
    public readonly ec2ServerRole: Role;

    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        this.ec2ServerRole = new Role(this, 'EC2ServerRole', {
            assumedBy: new ServicePrincipal('ec2.amazonaws.com'),
        });
    }
}