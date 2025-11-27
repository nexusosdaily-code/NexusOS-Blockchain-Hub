import os
import base64
import json
import requests

def get_github_token():
    """Get GitHub access token from Replit connector"""
    hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
    repl_identity = os.environ.get('REPL_IDENTITY')
    web_renewal = os.environ.get('WEB_REPL_RENEWAL')
    
    if repl_identity:
        x_replit_token = f'repl {repl_identity}'
    elif web_renewal:
        x_replit_token = f'depl {web_renewal}'
    else:
        raise ValueError("No Replit token found")
    
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
    token = settings.get('access_token') or settings.get('oauth', {}).get('credentials', {}).get('access_token')
    
    if not token:
        raise ValueError("GitHub not connected")
    
    return token

def update_file_on_github(token, owner, repo, path, content, message, branch="main"):
    """Update or create a file on GitHub"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Get current file SHA if exists
    url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
    params = {'ref': branch}
    response = requests.get(url, headers=headers, params=params)
    
    sha = None
    if response.status_code == 200:
        sha = response.json().get('sha')
    
    # Update or create file
    data = {
        'message': message,
        'content': base64.b64encode(content.encode()).decode(),
        'branch': branch
    }
    if sha:
        data['sha'] = sha
    
    response = requests.put(url, headers=headers, json=data)
    return response.status_code in [200, 201], response.json()

def main():
    token = get_github_token()
    owner = "nexusosdaily-code"
    repo = "WNSP-P2P-Hub"
    
    files_to_push = [
        ('wiki/WNSP-Protocol.md', 'Update WNSP Protocol documentation with v5.0 specs'),
        ('wiki/Home.md', 'Update wiki home with latest project stats'),
        ('wiki/Achievements.md', 'Update achievements with 37 breakthroughs'),
        ('wiki/Roadmap.md', 'Update roadmap with current v5.0 status'),
    ]
    
    results = []
    for file_path, message in files_to_push:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            success, response = update_file_on_github(token, owner, repo, file_path, content, message)
            results.append((file_path, success, response.get('commit', {}).get('sha', '')[:7] if success else str(response)))
            print(f"{'✓' if success else '✗'} {file_path}")
        except Exception as e:
            results.append((file_path, False, str(e)))
            print(f"✗ {file_path}: {e}")
    
    return results

if __name__ == '__main__':
    main()
