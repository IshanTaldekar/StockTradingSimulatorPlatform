import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Domain, EngineVersion} from "aws-cdk-lib/aws-opensearchservice";
import {EbsDeviceVolumeType, Vpc} from "aws-cdk-lib/aws-ec2";
import {AccountPrincipal, Effect, PolicyDocument, PolicyStatement, Role} from "aws-cdk-lib/aws-iam";

export interface OpenSearchServiceStackProps extends StackProps {
    readonly openSearchServiceAccessAccountRole: Role,
    readonly vpc: Vpc,
}

export class OpenSearchServiceStack extends Stack {
    constructor(scope: Construct, id: string, props: OpenSearchServiceStackProps) {
        super(scope, id, props);

        const opensearchServiceDomain = new Domain(this, 'Restaurants', {
            version: EngineVersion.ELASTICSEARCH_6_7,
            nodeToNodeEncryption: true,
            encryptionAtRest: {
                enabled: true
            },
            fineGrainedAccessControl: {
               masterUserName: 'master',
            },
            enforceHttps: true,
            domainName: 'restaurants',
            ebs: {
                volumeSize: 10,
                volumeType: EbsDeviceVolumeType.GP2
            },
            capacity: {
                dataNodeInstanceType: 't3.small.search',
                dataNodes: 1,
                multiAzWithStandbyEnabled: false,
            },
            zoneAwareness: {
                enabled: false
            },
            accessPolicies: [
                new PolicyStatement({
                    actions: [
                        'es:ESHttpPost',
                        'es:ESHttpPut',
                        'es:ESHttpGet',
                        'es:indices*'
                    ],
                    effect: Effect.ALLOW,
                    resources: ['*'],
                    principals: [
                        new AccountPrincipal(props.env?.account)
                    ],
                })
            ],
            vpc: props.vpc
        });
    }
}