import boto3
import json
import os

def get_execution_status(client, project, execution_id):
    response = client.get_pipeline_execution(
        pipelineName=project,
        pipelineExecutionId=execution_id
    )
    return response['pipelineExecution']['status']

def handler(event, context):

    project = event['queryStringParameters']['project'].replace('/', '.')
    execution_id = event['pathParameters']['id']

    client = boto3.client('codepipeline')

    status = get_execution_status(client, project, execution_id)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'status': status})
    }