import { StocksSimulatorStack } from '../lib/stocks_simulator-stack';
import {env} from "../lib/config";
import {App} from "aws-cdk-lib";

const app = new App();
new StocksSimulatorStack(app, 'StocksSimulator', {
    env: env
});