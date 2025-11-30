"""
Push updated documentation to GitHub repository.
Uses Replit's GitHub connection for authentication.
"""

import os
import json
import base64
import requests

def get_github_token():
    """Get GitHub access token from Replit connection."""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_repl_renewal:
        x_replit_token = f'depl {web_repl_renewal}'
    else:
        raise Exception('X_REPLIT_TOKEN not found')
    
    response = requests.get(
        f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=github',
        headers={
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
    )
    
    data = response.json()
    connection = data.get('items', [{}])[0]
    settings = connection.get('settings', {})
    
    access_token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    
    if not access_token:
        raise Exception('GitHub not connected')
    
    return access_token

def get_repo_info(token):
    """Get authenticated user's repos to find NexusOS repo."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get('https://api.github.com/user/repos?per_page=100', headers=headers)
    repos = response.json()
    
    for repo in repos:
        if 'nexus' in repo['name'].lower() or 'wnsp' in repo['name'].lower():
            return repo['owner']['login'], repo['name']
    
    return None, None

def get_file_sha(token, owner, repo, path):
    """Get the SHA of an existing file (needed for updates)."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo}/contents/{path}',
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json().get('sha')
    return None

def push_file(token, owner, repo, path, content, message):
    """Push a file to GitHub."""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    sha = get_file_sha(token, owner, repo, path)
    
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    
    data = {
        'message': message,
        'content': encoded_content
    }
    
    if sha:
        data['sha'] = sha
    
    response = requests.put(
        f'https://api.github.com/repos/{owner}/{repo}/contents/{path}',
        headers=headers,
        json=data
    )
    
    return response.status_code in [200, 201], response.json()

def main():
    print("Getting GitHub token...")
    token = get_github_token()
    print("✓ Token obtained")
    
    print("Finding NexusOS repository...")
    owner, repo = get_repo_info(token)
    
    if not owner or not repo:
        print("Repository not found. Listing available repos...")
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get('https://api.github.com/user/repos?per_page=100', headers=headers)
        repos = response.json()
        print("Available repositories:")
        for r in repos:
            print(f"  - {r['full_name']}")
        return
    
    print(f"✓ Found repository: {owner}/{repo}")
    
    files_to_push = [
        ('LAMBDA_BOSON_SUBSTRATE_MODEL.md', 'Update λ-Boson Substrate Model - real mass from oscillation, not quasiparticle'),
        ('LAYER_FUNCTIONALITY.md', 'Add NexusOS Layer Functionality documentation'),
        ('LAMBDA_BOSON_UNIFICATION.md', 'Update Lambda Boson Unification theory'),
    ]
    
    for filepath, message in files_to_push:
        if os.path.exists(filepath):
            print(f"\nPushing {filepath}...")
            with open(filepath, 'r') as f:
                content = f.read()
            
            success, result = push_file(token, owner, repo, filepath, content, message)
            
            if success:
                print(f"✓ {filepath} pushed successfully")
            else:
                print(f"✗ Failed to push {filepath}: {result.get('message', 'Unknown error')}")
        else:
            print(f"✗ File not found: {filepath}")
    
    print("\n✓ GitHub push complete")

if __name__ == '__main__':
    main()
