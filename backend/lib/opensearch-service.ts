import {Arn, ArnFormat, RemovalPolicy, Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Domain, EngineVersion} from "aws-cdk-lib/aws-opensearchservice";
import {EbsDeviceVolumeType} from "aws-cdk-lib/aws-ec2";
import {AccountPrincipal, ArnPrincipal, Effect, PolicyStatement} from "aws-cdk-lib/aws-iam";

export class OpenSearchServiceStack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps) {
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
            removalPolicy: RemovalPolicy.DESTROY
        });
    }
}