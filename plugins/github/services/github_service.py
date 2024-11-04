import os
import subprocess
from github import Github

def authenticate_github(token=None):
    return Github(token) if token else Github()

def get_all_stars(github, username):
    """Get all repositories starred by the user."""
    user = github.get_user(username)
    return [{"repo": repo.full_name, "url": repo.html_url} for repo in user.get_starred()]

def get_all_repo_stars_and_forks(github, username):
    """Get stars and forks for each repository owned by the user."""
    user = github.get_user(username)
    repo_data = {}
    for repo in user.get_repos():
        stargazers = [{"username": stargazer.login, "url": stargazer.html_url} for stargazer in repo.get_stargazers()]
        forks = [{"username": fork.owner.login, "url": fork.html_url} for fork in repo.get_forks()]
        repo_data[repo.name] = {
            "url": repo.html_url,
            "stargazers": stargazers,
            "forks": forks
        }
    return repo_data

def get_all_repo_branches_and_clone(github, username, clone_path="."):
    """Get all branches for each repository owned by the user and clone them."""
    user = github.get_user(username)
    repo_branches = {}
    for repo in user.get_repos():
        branches = [branch.name for branch in repo.get_branches()]
        repo_branches[repo.name] = {"url": repo.html_url, "branches": branches}
        clone_repo_all_branches(repo.clone_url, clone_path)
    return repo_branches

def get_all_followers(github, username):
    """Get all followers of the user."""
    user = github.get_user(username)
    return [{"username": follower.login, "url": follower.html_url} for follower in user.get_followers()]

def get_all_following(github, username):
    """Get all users followed by the user."""
    user = github.get_user(username)
    return [{"username": following.login, "url": following.html_url} for following in user.get_following()]

def get_all_commits_history(github, username):
    """Get commit history for all repositories owned by the user."""
    user = github.get_user(username)
    commit_history = {}
    for repo in user.get_repos():
        commits = [{"message": commit.commit.message, "url": commit.html_url} for commit in repo.get_commits()]
        commit_history[repo.name] = {"url": repo.html_url, "commits": commits}
    return commit_history

def get_all_activity(github, username):
    """Get recent activity of the user."""
    user = github.get_user(username)
    return [{"type": event.type, "repo": event.repo.name, "created_at": event.created_at.isoformat(), "details": event.payload} for event in user.get_events()]

def clone_repo_all_branches(repo_url, clone_path="."):
    """Clone a repository with all branches."""
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
