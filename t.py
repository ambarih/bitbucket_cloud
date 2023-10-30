import requests
import subprocess
import os

# Define your Bitbucket Server and Cloud details
SERVER_URL = 'http://localhost:7990'
CLOUD_URL = 'https://api.bitbucket.org/2.0'
SERVER_TOKEN = 'ATBBvme8jZkSftnVQLKzvgsanQBZ2A752038'
CLOUD_USERNAME = 'Ambarishg1'
CLOUD_PASSWORD = 'ATBBAVJpzURE9ymr4yR7xDDe3AFJ01DC2DCF'
WORKSPACE = 'danger1'

def list_projects():
    headers_server = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {SERVER_TOKEN}'
    }
    
    try:
        all_projects_and_repos = []

        # Fetch projects from the Bitbucket Server
        response_server = requests.get(f'{SERVER_URL}/rest/api/1.0/projects', headers=headers_server)
        response_server.raise_for_status()
        projects_data = response_server.json()

        for project in projects_data['values']:
            project_key = project['key']

            # Fetch repositories from the Bitbucket Server for each project
            response_server = requests.get(f'{SERVER_URL}/rest/api/1.0/projects/{project_key}/repos', headers=headers_server)
            response_server.raise_for_status()
            repositories_data = response_server.json()
            project_info = {
                'project_name': project['name'],
                'repositories': repositories_data['values']
            }
            all_projects_and_repos.append(project_info)

        return all_projects_and_repos

    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to fetch data from Bitbucket Server: {str(e)}'}

def create_projects_and_repositories_in_cloud(project_data, cloud_url):
    try:
        for project_info in project_data:
            # Create a project in Bitbucket Cloud
            project_name = project_info['project_name']
            cloud_project_data = {'key': project_info['project_name'], 'is_private': False, 'name': project_name}
            response_cloud_project = requests.post(f'{cloud_url}/workspaces/{WORKSPACE}/projects', 
                                                   auth=(CLOUD_USERNAME, CLOUD_PASSWORD),
                                                   json=cloud_project_data)
            response_cloud_project.raise_for_status()

            # Create repositories in Bitbucket Cloud for each project
            for repo in project_info['repositories']:
                repo_name = repo['name']
                cloud_repo_data = {'scm': 'git', 'is_private': False, 'project': {'key': project_name}, 'name': repo_name}
                response_cloud_repo = requests.post(f'{cloud_url}/repositories/{WORKSPACE}/{repo_name}', 
                                                   auth=(CLOUD_USERNAME, CLOUD_PASSWORD),
                                                   json=cloud_repo_data)
                response_cloud_repo.raise_for_status()

        return {'message': 'Projects and repositories successfully created in Bitbucket Cloud'}

    except requests.exceptions.RequestException as e:
        return {'error': f'Failed to create projects and repositories in Bitbucket Cloud: {str(e)}'}

def mirror_repositories(project_data):
    try:
        for project_info in project_data:
            # Clone repositories from Bitbucket Server to a local directory
            for repo in project_info['repositories']:
                repo_name = repo['name']
                local_repo_path = f'./{project_info["project_name"]}/{repo_name}'
                if not os.path.exists(local_repo_path):
                    os.makedirs(local_repo_path)
                subprocess.run(['git', 'clone', f'{SERVER_URL}/scm/{project_info["project_name"]}/{repo_name}.git', local_repo_path])

                # Add a remote for the Bitbucket Cloud repository
                subprocess.run(['git', 'remote', 'add', 'cloud', f'https://{CLOUD_USERNAME}@bitbucket.org/{WORKSPACE}/{repo_name}.git'], cwd=local_repo_path)

                # Push to Bitbucket Cloud using the git mirror command
                subprocess.run(['git', 'push', '--mirror', 'cloud'], cwd=local_repo_path)

        return {'message': 'Projects and repositories successfully mirrored to Bitbucket Cloud'}

    except Exception as e:
        return {'error': f'Failed to mirror repositories to Bitbucket Cloud: {str(e)}'}

if __name__ == '__main__':
    project_data = list_projects()
    if 'error' in project_data:
        print(project_data['error'])
    else:
        CLOUD_URL = 'https://api.bitbucket.org/2.0'
        create_result = create_projects_and_repositories_in_cloud(project_data, CLOUD_URL)
        if 'error' in create_result:
            print(create_result['error'])
        else:
            print(create_result['message'])
            mirror_result = mirror_repositories(project_data)
            if 'error' in mirror_result:
                print(mirror_result['error'])
            else:
                print('Projects and repositories successfully mirrored to Bitbucket Cloud')