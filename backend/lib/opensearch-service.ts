import {Arn, ArnFormat, Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Domain, EngineVersion} from "aws-cdk-lib/aws-opensearchservice";
import {EbsDeviceVolumeType, Vpc} from "aws-cdk-lib/aws-ec2";
import {AccountPrincipal, ArnPrincipal, Effect, PolicyStatement} from "aws-cdk-lib/aws-iam";

export interface OpenSearchServiceStackProps extends StackProps {
    readonly vpc: Vpc,
}

export class OpenSearchServiceStack extends Stack {
    constructor(scope: Construct, id: string, props: OpenSearchServiceStackProps) {
        super(scope, id, props);

        const opensearchServiceDomain = new Domain(this, 'NewsSummary', {
            version: EngineVersion.ELASTICSEARCH_6_7,
            nodeToNodeEncryption: true,
            encryptionAtRest: {
                enabled: true
            },
            fineGrainedAccessControl: {
               masterUserName: 'master',
            },
            enforceHttps: true,
            domainName: 'news-summary',
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
                    resources: [
                        Arn.format(
                            {
                                arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                service: 'es',
                                resource: 'domain',
                                resourceName: 'news-summary/*',
                            },
                            this
                        )
                    ],
                    principals: [
                        new ArnPrincipal(
                            Arn.format(
                                {
                                    arnFormat: ArnFormat.SLASH_RESOURCE_NAME,
                                    service: 'iam',
                                    resource: 'user',
                                    resourceName: 'ishantaldekar',
                                    region: ''
                                },
                                this
                            )
                        ),
                        new AccountPrincipal(props.env?.account)
                    ],
                })
            ],
            vpc: props.vpc
        });
    }
}