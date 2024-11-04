import json
from plugins.plugin_base import Plugin
from plugins.github.services.github_service import (
    authenticate_github,
    get_all_stars,
    get_all_repo_stars_and_forks,
    get_all_repo_branches_and_clone,
    get_all_followers,
    get_all_following,
    get_all_commits_history,
    get_all_activity,
    clone_repo_all_branches,
)

class Handler(Plugin):
    def register_as(self):
        return "github"

    def commands(self, subparsers):
        github_parser = subparsers.add_parser(self.register_as(), help="GitHub related commands")
        github_subparsers = github_parser.add_subparsers(dest="action", required=True)

        github_subparsers.add_parser("all_stars", help="Get all stars from user").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_repo_stars_and_forks", help="Get all repo stars and forks for user").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_repo_branches_and_clone", help="Get all branches and clone all repos").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_followers", help="Get all followers of the user").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_following", help="Get all users followed by the user").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_commits_history", help="Get commit history for all repos").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )
        github_subparsers.add_parser("all_activity", help="Get all recent activities of user").add_argument(
            "--username", type=str, required=True, help="GitHub username to analyze"
        )

        clone_parser = github_subparsers.add_parser("clone_single_repo_all_branches", help="Clone a single repo with all branches")
        clone_parser.add_argument("repo_url", type=str, help="URL of the GitHub repository to clone")
        clone_parser.add_argument("--clone-path", type=str, default=".", help="Directory to save cloned repositories")

        aggregate_parser = github_subparsers.add_parser("aggregate", help="Perform all OSINT operations with optional repository cloning")
        aggregate_parser.add_argument("--username", type=str, required=True, help="GitHub username to analyze")
        aggregate_parser.add_argument("--clone-path", type=str, default=".", help="Directory to save cloned repositories if --download is set")
        aggregate_parser.add_argument("--download", action="store_true", help="Flag to download all repositories with all branches")

    def handle(self, args):
        # Public data fetch, so no authentication unless requested
        github = authenticate_github()  # Pass an empty or None token for public access

        action_map = {
            "all_stars": lambda: self._handle_all_stars(github, args),
            "all_repo_stars_and_forks": lambda: self._handle_all_repo_stars_and_forks(github, args),
            "all_repo_branches_and_clone": lambda: self._handle_all_repo_branches_and_clone(github, args),
            "all_followers": lambda: self._handle_all_followers(github, args),
            "all_following": lambda: self._handle_all_following(github, args),
            "all_commits_history": lambda: self._handle_all_commits_history(github, args),
            "all_activity": lambda: self._handle_all_activity(github, args),
            "clone_single_repo_all_branches": lambda: self._handle_clone_single_repo(github, args),
            "aggregate": lambda: self._handle_aggregate(github, args)
        }

        if args.action in action_map:
            action_map[args.action]()

    # Individual handlers for OSINT tasks
    def _handle_all_stars(self, github, args):
        data = get_all_stars(github, args.username)
        self._save_json(data, f"{args.username}_all_stars.json")

    def _handle_all_repo_stars_and_forks(self, github, args):
        data = get_all_repo_stars_and_forks(github, args.username)
        self._save_json(data, f"{args.username}_all_repo_stars_and_forks.json")

    def _handle_all_repo_branches_and_clone(self, github, args):
        data = get_all_repo_branches_and_clone(github, args.username, args.clone_path)
        self._save_json(data, f"{args.username}_all_repo_branches.json")

    def _handle_all_followers(self, github, args):
        data = get_all_followers(github, args.username)
        self._save_json(data, f"{args.username}_all_followers.json")

    def _handle_all_following(self, github, args):
        data = get_all_following(github, args.username)
        self._save_json(data, f"{args.username}_all_following.json")

    def _handle_all_commits_history(self, github, args):
        data = get_all_commits_history(github, args.username)
        self._save_json(data, f"{args.username}_all_commits_history.json")

    def _handle_all_activity(self, github, args):
        data = get_all_activity(github, args.username)
        self._save_json(data, f"{args.username}_all_activity.json")

    def _handle_clone_single_repo(self, github, args):
        clone_repo_all_branches(args.repo_url, args.clone_path)
        print(f"Cloned {args.repo_url} with all branches to {args.clone_path}")

    def _handle_aggregate(self, github, args):
        print("Performing OSINT aggregation for user:", args.username)

        self._handle_all_stars(github, args)
        self._handle_all_repo_stars_and_forks(github, args)
        self._handle_all_followers(github, args)
        self._handle_all_following(github, args)
        self._handle_all_commits_history(github, args)
        self._handle_all_activity(github, args)

        if args.download:
            print("Cloning all repositories with all branches...")
            get_all_repo_branches_and_clone(github, args.username, args.clone_path)
        else:
            print("Skipping repository cloning (use --download to enable).")

    def _save_json(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {filename}")
