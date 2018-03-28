#!/usr/bin/env python3.6
import os
import logging
import aws_lambda_logging
import json
import uuid
from dateutil.tz import tzlocal, tzutc
import datetime
import boto3

aws_lambda_logging.setup(level=os.environ.get('LOGLEVEL', 'INFO'), env=os.environ.get('ENV'))
logging.info(json.dumps({'message': 'initialising'}))
aws_lambda_logging.setup(level=os.environ.get('LOGLEVEL', 'INFO'), env=os.environ.get('ENV'))


def handler(event, context):
    """Handler for serverless-ecs-metrics"""
    aws_lambda_logging.setup(level=os.environ.get('LOGLEVEL', 'INFO'), env=os.environ.get('ENV'))
    ecs = boto3.client('ecs')
    cloudwatch = boto3.client('cloudwatch')

    clusters = [x.split('/')[-1] for x in ecs.list_clusters()['clusterArns']]
    logging.info(json.dumps({'message': 'getting clusters', 'clusters': clusters}))

    MetricData = []
    for cluster in clusters:
        metrics = []
        cpu = None
        mem = None
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='MemoryReservation',
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
                EndTime=datetime.datetime.utcnow(),
                Period=300,
                Statistics=['Average'],
                Dimensions=[{'Name': 'ClusterName', 'Value': cluster}]
            )
            mem = response['Datapoints'][0]['Average']
            logging.info(json.dumps({"message": "getting memory", "mem": mem}))
        except:
            logging.exception(json.dumps({"message": "getting memory", "response": response}))

        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/ECS',
                MetricName='CPUReservation',
                StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
                EndTime=datetime.datetime.utcnow(),
                Period=300,
                Statistics=['Average'],
                Dimensions=[{'Name': 'ClusterName', 'Value': cluster}]
            )
            cpu = response['Datapoints'][0]['Average']
            logging.info(json.dumps({"message": "getting cpu", "cpu": cpu}))
        except:
            logging.exception(json.dumps({"message": "getting cpu", "response": response}))

        if cpu and mem:
            combined = max([cpu, mem])

            MetricData.append({
                'MetricName': 'CombinedReservation',
                'Dimensions': [{'Name': 'ClusterName', 'Value': cluster}],
                'Value': combined,
                'Unit': 'Percent'
            })

    logging.debug(json.dumps(MetricData))

    cloudwatch.put_metric_data(
        Namespace='ECS',
        MetricData=MetricData
    )

    return

