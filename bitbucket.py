from flask import Flask, request
from flask_restx import Api, Resource, reqparse,fields
import requests
import json

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='Bitbucket Cloud Microservice API',
    description='Microservice for Bitbucket Cloud integration'
)

create_project_parser = reqparse.RequestParser()
create_project_parser.add_argument('bitbucket_cloud_workspace', type=str, required=True, help='Workspace name')
create_project_parser.add_argument('bitbucket_cloud_project_key', type=str, required=True, help='Project Key')
create_project_parser.add_argument('bitbucket_cloud_project_name', type=str, required=True, help='Project Name')
create_project_parser.add_argument('bitbucket_cloud_username', type=str, required=True, help='Bitbucket Cloud username')
create_project_parser.add_argument('bitbucket_cloud_password', type=str, required=True, help='Bitbucket Cloud password')
create_project_parser.add_argument('bitbucket_cloud_url', type=str, required=True, help='Bitbucket Cloud API URL')

class BitbucketCloudProjects2(Resource):
    @api.expect(create_project_parser)
    def post(self):
        """Create a new Bitbucket Cloud project"""
        args = create_project_parser.parse_args()
        workspace = args['workspace']
        project_key = args['project_key']
        project_name = args['project_name']
        username = args['username']
        password = args['password']
        bitbucket_url = args['bitbucket_url']

        auth = (username, password)

        project_create_url = f"{bitbucket_url}workspaces/{workspace}/projects/"
        new_project_data = {
            "name": project_name,
            "key": project_key,
            "description": ""  # You can add a description if needed
        }

        response = requests.post(project_create_url, json=new_project_data, auth=auth)

        if response.status_code == 201:
            return {'message': 'New Bitbucket Cloud project created successfully'}
        else:
            return {'message': 'Error creating Bitbucket Cloud project'}, response.status_code


repo_parser = reqparse.RequestParser()
repo_parser.add_argument('bitbucket_cloud_workspace', type=str, required=True, help='Workspace name')
repo_parser.add_argument('bitbucket_cloud_repo_name', type=str, required=True, help='Name of the repository')
repo_parser.add_argument('bitbucket_cloud_description', type=str, help='Description of the repository')
repo_parser.add_argument('bitbucket_cloud_project_key', type=str, required=True, help='Project Key')
repo_parser.add_argument('bitbucket_cloud_username', type=str, required=True, help='Bitbucket Cloud username')
repo_parser.add_argument('bitbucket_cloud_password', type=str, required=True, help='Bitbucket Cloud password')
repo_parser.add_argument('bitbucket_cloud_url', type=str, required=True, help='Bitbucket API URL')

class BitbucketCloudRepositories3(Resource):
    @api.expect(repo_parser)
    def post(self):
        """Create a new Bitbucket Cloud repository under a specific project"""
        args = repo_parser.parse_args()
        bitbucket_url = f"{args['bitbucket_url']}/repositories/{args['workspace']}/{args['repo_name']}"
        username = args['username']
        password = args['password']
        auth = (username, password)
        new_repo_data = {
            "scm": "git",
            "is_private": False,
            "name": args['repo_name'],
            "description": args['description'],
            "project": {"key": args["project_key"]}
        }
        response = requests.post(bitbucket_url, json=new_repo_data, auth=auth)
        if response.status_code == 200:
            return {'message': 'New Bitbucket Cloud repository created successfully'}
        else:
            return {'message': 'Error creating Bitbucket Cloud repository'}, response.status_code

get_parser = reqparse.RequestParser()
get_parser.add_argument('bitbucket_cloud__url', type=str, required=True, help='Bitbucket API URL')
get_parser.add_argument('bitbucket_cloud_username', type=str, required=True, help='Bitbucket username')
get_parser.add_argument('bitbucket_cloud_password', type=str, required=True, help='Bitbucket password')
get_parser.add_argument('bitbucket_cloud_workspace', type=str, required=True, help='Bitbucket workspace')
get_parser.add_argument('bitbucket_cloud_repo_name', type=str, required=True, help='Bitbucket repository name')

class BitbucketCloudRepositories(Resource):
    @api.expect(get_parser)
    def get(self):
        """Get information about a Bitbucket Cloud repository in a workspace"""
        args = get_parser.parse_args()
        bitbucket_url = args['bitbucket_url']
        username = args['username']
        password = args['password']
        workspace = args['workspace']
        repo_name = args['repo_name']

        bitbucket_url = f'{bitbucket_url}/repositories/{workspace}/{repo_name}' 
        auth = (username, password)
        response = requests.get(bitbucket_url, auth=auth)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {'message': 'Workspace or repository not found', 'status_code': 404}
        else:
            return {'message': f'Error getting Bitbucket Cloud repository {repo_name}', 'status_code': response.status_code}


delete_project_parser = reqparse.RequestParser()
delete_project_parser.add_argument('bitbucket_cloud__url', type=str, required=True, help='Bitbucket API URL')
delete_project_parser.add_argument('bitbucket_cloud_username', type=str, required=True, help='Bitbucket username')
delete_project_parser.add_argument('bitbucket_cloud_password', type=str, required=True, help='Bitbucket password')
delete_project_parser.add_argument('bitbucket_cloud_workspace', type=str, required=True, help='Bitbucket workspace')
delete_project_parser.add_argument('bitbucket_cloud_project_key', type=str, required=True, help='Bitbucket project key')

class BitbucketCloudProjects(Resource):
    @api.expect(delete_project_parser)
    def delete(self):
        """Delete a Bitbucket Cloud project"""
        args = delete_project_parser.parse_args()
        bitbucket_url = args['bitbucket_url']
        username = args['username']
        password = args['password']
        workspace = args['workspace']
        project_key = args['project_key']
        bitbucket_url = f'{bitbucket_url}/workspaces/{workspace}/projects/{project_key}'

        auth = (username, password)
        response = requests.delete(bitbucket_url, auth=auth)

        if response.status_code == 204:
            return {'message': f'Bitbucket Cloud project {project_key} in workspace {workspace} deleted successfully', 'status_code': 204}
        elif response.status_code == 404:
            return {'message': 'Project not found', 'status_code': 404}
        else:
            return {'message': f'Error deleting Bitbucket Cloud project {project_key}', 'status_code': response.status_code}
delete_parser = reqparse.RequestParser()
delete_parser.add_argument('bitbucket_cloud_url', type=str, required=True, help='Bitbucket API URL')
delete_parser.add_argument('bitbucket_cloud_username', type=str, required=True, help='Bitbucket username')
delete_parser.add_argument('bitbucket_cloud_password', type=str, required=True, help='Bitbucket password')

delete_response_model = api.model('DeleteResponse', {
    'message': fields.String(description='Status message'),
    'status_code': fields.Integer(description='HTTP status code')
})

class BitbucketCloudRepositories1(Resource):
    @api.expect(delete_parser)
    @api.marshal_with(delete_response_model, code=200)
    def delete(self, workspace, repo_name):
        """Delete a Bitbucket Cloud repository in a workspace"""
        args = delete_parser.parse_args()
        bitbucket_url = args['bitbucket_url']
        username = args['username']
        password = args['password']
        
        bitbucket_url = f'{bitbucket_url}/repositories/{workspace}/{repo_name}' 
        auth = (username, password)
        response = requests.delete(bitbucket_url, auth=auth)
        
        if response.status_code == 204:
            return {'message': f'Bitbucket Cloud repository {repo_name} in the workspace deleted successfully', 'status_code': 204}
        elif response.status_code == 404:
            return {'message': 'Workspace or repository not found', 'status_code': 404}
        else:
            return {'message': f'Error deleting Bitbucket Cloud repository {repo_name}', 'status_code': response.status_code}

api.add_resource(BitbucketCloudRepositories1, '/repositories/<string:workspace>/<string:repo_name>/')
api.add_resource(BitbucketCloudRepositories, '/repositories/get')
api.add_resource(BitbucketCloudProjects, '/projects/delete')
api.add_resource(BitbucketCloudRepositories3, '/repositories/')
api.add_resource(BitbucketCloudProjects2, '/workspaces/{workspace}/projects/')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)