import os
import subprocess
from github import Github

def authenticate_github(token=None):
    return Github(token) if token else Github()

def get_all_stars(github, username):
    user = github.get_user(username)
    stars = [{"repo": repo.full_name, "url": repo.html_url, "description": repo.description} for repo in user.get_starred()]
    return stars

def get_all_repo_stars_and_forks(github, username):
    user = github.get_user(username)
    repo_data = []
    for repo in user.get_repos():
        stargazers = [{"username": stargazer.login, "url": stargazer.html_url} for stargazer in repo.get_stargazers()]
        forks = [{"username": fork.owner.login, "url": fork.html_url} for fork in repo.get_forks()]
        repo_info = {
            "repo_name": repo.name,
            "url": repo.html_url,
            "description": repo.description,
            "stargazers_count": len(stargazers),
            "forks_count": len(forks)
        }
        repo_data.append(repo_info)
    return repo_data

def get_all_repo_branches_and_clone(github, username, clone_path="."):
    user = github.get_user(username)
    branches_data = []
    for repo in user.get_repos():
        branches = [branch.name for branch in repo.get_branches()]
        branches_data.append({
            "repo_name": repo.name,
            "url": repo.html_url,
            "description": repo.description,
            "branches": ", ".join(branches)
        })
        clone_repo_all_branches(repo.clone_url, clone_path)
    return branches_data

def get_all_followers(github, username):
    user = github.get_user(username)
    followers = [{"username": follower.login, "url": follower.html_url} for follower in user.get_followers()]
    return followers

def get_all_following(github, username):
    user = github.get_user(username)
    following = [{"username": following.login, "url": following.html_url} for following in user.get_following()]
    return following

def get_all_commits_history(github, username):
    user = github.get_user(username)
    commit_data = []
    for repo in user.get_repos():
        commits = [{"message": commit.commit.message, "url": commit.html_url} for commit in repo.get_commits()]
        for commit in commits:
            commit_data.append({
                "repo_name": repo.name,
                "url": repo.html_url,
                "description": repo.description,
                "commit_message": commit["message"],
                "commit_url": commit["url"]
            })
    return commit_data

def get_all_activity(github, username):
    user = github.get_user(username)
    activity = [{"type": event.type, "repo": event.repo.name, "created_at": event.created_at.isoformat(), "details": event.payload} for event in user.get_events()]
    return activity

def clone_repo_all_branches(repo_url, clone_path="."):
    repo_name = repo_url.split("/")[-1]
    repo_path = os.path.join(clone_path, repo_name)
    
    if not os.path.exists(clone_path):
        os.makedirs(clone_path)

    if not os.path.exists(repo_path):
        subprocess.run(["git", "clone", repo_url, repo_path])

    subprocess.run(["git", "fetch", "--all"], cwd=repo_path)

    branches = subprocess.run(["git", "branch", "-r"], cwd=repo_path, capture_output=True, text=True)
    remote_branches = branches.stdout.strip().split('\n')
    for branch in remote_branches:
        branch_name = branch.strip().replace("origin/", "")
        if branch_name != "HEAD":
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=repo_path)
