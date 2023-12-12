import {Stack, StackProps} from "aws-cdk-lib";
import {Construct} from "constructs";
import {AccountRecovery, UserPool, VerificationEmailStyle} from "aws-cdk-lib/aws-cognito";
import {Role} from "aws-cdk-lib/aws-iam";
import { IdentityPool } from "@aws-cdk/aws-cognito-identitypool-alpha";

export interface CognitoStackProps extends StackProps {
    readonly ec2ServerRole: Role,
    readonly identityPoolAuthenticatedRole: Role,
    readonly identityPoolUnauthenticatedRole: Role,
}

export class CognitoStack extends Stack {
    constructor(scope: Construct, id: string, props: CognitoStackProps) {
        super(scope, id, props);

        const userPool = new UserPool(this, 'StockSimulatorUserPool', {
            userPoolName: 'stock-simulator-user-pool',
            selfSignUpEnabled: true,
            userVerification: {
                emailSubject: 'Verify your email for PlayStonks!',
                emailBody: 'Thanks for signing up to PlayStonks! Your verification code is {####}',
                emailStyle: VerificationEmailStyle.CODE,
                smsMessage: 'Thanks for signing up to PlayStonks! Your verification code is {####}'
            },
            signInAliases: {
                username: true,
                email: true,
                phone: true
            },
            standardAttributes: {
                email: {
                    required: true,
                    mutable: true
                },
                phoneNumber: {
                    required: true,
                    mutable: true
                }
            },
            autoVerify: {
                email: true,
                phone: true
            },
            keepOriginal: {
                email: true,
                phone: true
            },
            accountRecovery: AccountRecovery.EMAIL_ONLY
        });
        userPool.grant(props.ec2ServerRole, 'cognito-idp:AdminCreateUser');
    }
}