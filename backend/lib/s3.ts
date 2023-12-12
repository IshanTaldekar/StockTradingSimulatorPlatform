import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {Bucket} from "aws-cdk-lib/aws-s3";

export class S3Stack extends Stack {
    constructor(scope: Construct, id: string, props: StackProps) {
        super(scope, id, props);

        const websiteCodeBucket = new Bucket(this, 'WebsiteCodeS3Bucket', {
            bucketName: 'cloud-computing-project-website-code-bucket'
        });
    }
}