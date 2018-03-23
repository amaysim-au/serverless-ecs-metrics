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

ecs = boto3.client('ecs')
cloudwatch = boto3.client('cloudwatch')
MetricData = []

def handler(event, context):
    """Handler for serverless-ecs-metrics"""
    aws_lambda_logging.setup(level=os.environ.get('LOGLEVEL', 'INFO'), env=os.environ.get('ENV'))

    clusters = [x.split('/')[-1] for x in ecs.list_clusters()['clusterArns']]

    for cluster in clusters:
        metrics = []
        mem = cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='MemoryReservation',
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
            EndTime=datetime.datetime.utcnow(),
            Period=300, 
            Statistics=['Average'],
            Dimensions=[{'Name': 'ClusterName', 'Value': cluster}]
        )['Datapoints'][0]['Average']
        cpu = cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='CPUReservation',
            StartTime=datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
            EndTime=datetime.datetime.utcnow(),
            Period=300, 
            Statistics=['Average'],
            Dimensions=[{'Name': 'ClusterName', 'Value': cluster}]
        )['Datapoints'][0]['Average']

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

