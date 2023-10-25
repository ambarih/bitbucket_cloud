import requests
import git

# Bitbucket Cloud credentials
cloud_username = 'Ambarishg1'
cloud_password = 'ATBBJk9MnWLCrZVn29CUGCgYXMkVF63FAE3F'
cloud_org = 'danger1'

# Bitbucket Server credentials and bearer token
server_url = 'https://git.altimetrik.com'
projectKey = 'OA'
server_bearer_token = 'MzQwMjk2NTc4Mjc2OmeDiWobi9voYk3m5B23gXyMRm44'

cloud_auth = (cloud_username, cloud_password)

cloud_project_url = f'https://api.bitbucket.org/2.0//workspaces/{cloud_org}/projects/{projectKey}'
cloud_project_data = {
    # "key": projectKey,
    "name": "Your ", 
    "description": "Migrated from Bitbucket Server"
}
cloud_project_response = requests.put(cloud_project_url, json=cloud_project_data, auth=cloud_auth)

if cloud_project_response.status_code != 200 and cloud_project_response.status_code != 201:
    print(f"Failed to create Bitbucket Cloud project: {projectKey}")
    print(f"Status Code: {cloud_project_response.status_code}")
    print(f"Response Content: {cloud_project_response.content}")
    exit(1)

# Step 2: Get repositories from Bitbucket Server using Bearer Token
headers = {"Authorization": f"Bearer {server_bearer_token}"}
server_repos_url = f'{server_url}/bitbucket/rest/api/1.0/projects/{projectKey}/repos'
server_repos_response = requests.get(server_repos_url, headers=headers)

if server_repos_response.status_code != 200:
    print(f"Failed to fetch repositories from Bitbucket Server. Status Code: {server_repos_response.status_code}")
    print(f"Response Content: {server_repos_response.content}")
    exit(1)
server_repos_data = server_repos_response.json()

# Step 3: Migrate repositories to Bitbucket Cloud
for server_repo in server_repos_data['values']:
    repo_name = server_repo['name']

    # Create Bitbucket Cloud repository in the same project
    cloud_project_key = projectKey  # Use the same project key
    cloud_repo_name = repo_name  # Use the same repo name
    cloud_repo_data = {
        "scm": "git",
        "is_private": False,
        "project": {"key": cloud_project_key},
        "name": cloud_repo_name,
        "description": "Migrated from Bitbucket Server"
    }
    cloud_repo_url = f'https://api.bitbucket.org/2.0/repositories/{cloud_org}/{cloud_repo_name}'
    cloud_repo_response = requests.post(cloud_repo_url, json=cloud_repo_data, auth=cloud_auth)

    if cloud_repo_response.status_code != 201:
        print(f"Failed to create Bitbucket Cloud repository: {cloud_repo_name}")
        print(f"Status Code: {cloud_repo_response.status_code}")
        print(f"Response Content: {cloud_repo_response.content}")
        exit(1)

    try:
        # Clone the Bitbucket Server repository using GitPython
        server_repo_url = f'{server_url}/scm/{projectKey}/{repo_name}.git'
        local_repo_path = f'./{projectKey}/{repo_name}'
        server_repo = git.Repo.clone_from(server_repo_url, local_repo_path)

        # Add the Bitbucket Cloud repository as a remote
        cloud_repo_path = f'https://{cloud_username}@bitbucket.org/{cloud_org}/{cloud_project_key}/{cloud_repo_name}.git'
        server_repo.create_remote('cloud', cloud_repo_path)

        # Push code to Bitbucket Cloud
        server_repo.remotes.cloud.push()

        # Clean up the local repository
        server_repo.close()
    except Exception as e:
        # Handle Git operations errors
        print(f"Error during Git operations: {str(e)}")
        exit(1)

print("Migration successful")