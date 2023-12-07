#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StocksSimulatorStack } from '../lib/stocks_simulator-stack';
import {env} from "../lib/config";

const app = new cdk.App();
new StocksSimulatorStack(app, 'StocksSimulatorStack', {
    env: env
});