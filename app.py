from flask import Flask, request
from flask_restx import Api, Resource, reqparse
import subprocess
import os

app = Flask(__name__)
api = Api(
    app,
    version='1.0',
    title='Git Repository Migration API',
    description='API for cloning and pushing repositories'
)

# Request parser for Git operations
git_operation_parser = reqparse.RequestParser()
git_operation_parser.add_argument('server_repo_url', type=str, required=True, help='Bitbucket Server Repository URL')
git_operation_parser.add_argument('cloud_repo_url', type=str, required=True, help='Bitbucket Cloud Repository URL')

class GitMigration(Resource):
    @api.expect(git_operation_parser)
    def post(self):
        """Clone Bitbucket Server repo and push to Bitbucket Cloud"""
        args = git_operation_parser.parse_args()
        server_repo_url = args['server_repo_url']
        cloud_repo_url = args['cloud_repo_url']

        clone_directory = "bitbucket_server_clone"
        try:
            subprocess.run(["git", "clone", server_repo_url, clone_directory])
        except subprocess.CalledProcessError as e:
            return {'message': f"Error cloning Bitbucket Server repository: {e}"}, 500

        os.chdir(clone_directory)

        try:
            subprocess.run(["git", "remote", "add", "bitbucket_cloud", cloud_repo_url])
        except subprocess.CalledProcessError as e:
            return {'message': f"Error adding Bitbucket Cloud repository as a remote: {e}"}, 500

        try:
            subprocess.run(["git", "push", "bitbucket_cloud", "master"])
        except subprocess.CalledProcessError as e:
            return {'message': f"Error pushing code to Bitbucket Cloud: {e}"}, 500

        return {'message': "Repository cloned from Bitbucket Server and pushed to Bitbucket Cloud successfully"}, 200

api.add_resource(GitMigration, '/git-migration')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
