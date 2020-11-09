import boto3
import json
import os

"""
Post Data
{
    "Project": "name/repo",
    "Branch": "develop",
    "Stages": JSON
}
"""

def stages(repo, branch):
    client = boto3.client('ssm')
    resp = client.get_parameter(Name='/pipelinery/github/token', WithDecryption=True)
    token = resp['Parameter']['Value']
    return [
        {
            'name': 'Source',
            'actions': [
                {
                    'name': 'GitHub',
                    'actionTypeId': {
                        'category': 'Source',
                        'owner': 'ThirdParty',
                        'provider': 'GitHub',
                        'version': '1'
                    },
                    'outputArtifacts': [
                        {
                            'name': 'Source'
                        }
                    ],
                    'configuration': {
                        'Owner': repo.split('.')[0],
                        'Repo': repo.split('.')[1],
                        'Branch': branch,
                        'PollForSourceChanges': 'False',
                        'OAuthToken': token
                    }
                }
            ]
        },
        {
            'name': 'Deploy',
            'actions': [
                {
                    'name': 'CreateChangeSet',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': 'CloudFormation',
                        'version': '1'
                    },
                    'configuration': {
                        'ChangeSetName': 'pipelinery',
                        'ActionMode': 'CHANGE_SET_REPLACE',
                        'StackName': f"{repo.split('.')[1]}-{branch.replace('/', '-')}",
                        'Capabilities': 'CAPABILITY_IAM',
                        'TemplatePath': 'Source::template.yaml',
                        'RoleArn': os.environ['CLOUDFORMATION_ROLE_ARN']
                    },
                    'inputArtifacts': [
                        {
                            'name': 'Source'
                        }
                    ],
                    'runOrder': 1
                },
                {
                    'name': 'ExecuteChangeSet',
                    'actionTypeId': {
                        'category': 'Deploy',
                        'owner': 'AWS',
                        'provider': 'CloudFormation',
                        'version': '1'
                    },
                    'configuration': {
                        'ChangeSetName': 'pipelinery',
                        'ActionMode': 'CHANGE_SET_EXECUTE',
                        'StackName': f"{repo.split('.')[1]}-{branch.replace('/', '-')}",
                        'RoleArn': os.environ['CLOUDFORMATION_ROLE_ARN']
                    },
                    'runOrder': 1
                }
            ]
        }
    ]

def pipeline_exists(client, name):
    try:
        client.get_pipeline(name=name)
        return True
    except client.exceptions.PipelineNotFoundException:
        return False

def create_pipeline(client, name, branch):
    client.create_pipeline(
        pipeline={
            'name': name,
            'roleArn': os.environ['CODEPIPELINE_ROLE_ARN'],
            'artifactStore': {
                'type': 'S3',
                'location': os.environ['ARTIFACT_BUCKET'],
            },
            'stages': stages(name, branch)
        },
        tags=[
            {
                'key': 'pipelinery:project',
                'value': name
            }
        ]
    )

def update_pipeline(client, name, branch):
    client.update_pipeline(
        pipeline={
            'name': name,
            'roleArn': os.environ['CODEPIPELINE_ROLE_ARN'],
            'artifactStore': {
                'type': 'S3',
                'location': os.environ['ARTIFACT_BUCKET'],
            },
            'stages': stages(name, branch)
        }
    )

def execute_pipeline(client, name):
    response = client.start_pipeline_execution(
        name=name
    )
    return response['pipelineExecutionId']

# POST
def handler(event, context):

    body = json.loads(event['body'])
    project = body['Project'].replace('/', '.')
    branch = body['Branch']

    client = boto3.client('codepipeline')

    if pipeline_exists(client, project):
        update_pipeline(client, project, branch)
    else:
        create_pipeline(client, project, branch)

    execution_id = execute_pipeline(client, project)

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({'executionId': execution_id})
    }