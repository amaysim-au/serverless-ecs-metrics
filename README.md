# Serverless ECS Metrics
Created with [Serverless Python Boilerplate](https://github.com/amaysim-au/serverless-python-boilerplate)

Creates a 3rd metric for ECS Clusters which is the greater of ECS/CPUReservation and ECS/MemoryReservation. Used to scale in ECS clusters.

## Deploying
To install the required NPM modules for Serverless:
```
make deps
```
To create the virtualenv, install requirements using pip and then create the package.zip for uploading to Lambda:
```
make build
```
To deploy, fill out your `.env` file and then:
```
make deploy
```
