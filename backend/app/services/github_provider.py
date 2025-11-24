import os
import base64
import concurrent.futures
from typing import Optional, List, Dict, Any
from github import Github, GithubException, UnknownObjectException
from app.core.interfaces import IGithubProvider
from app.models.dtos import UserProfile, Repository

class GithubProvider(IGithubProvider):
    """
    Concrete implementation of IGithubProvider using PyGithub.
    Refactored to be a pure, high-performance data fetcher.
    """
    
    def __init__(self, token: Optional[str] = None):
        self.client = Github(token)
        self.max_workers = 10  # Optimize for I/O bound tasks

    def _fetch_content(self, repo, filepath: str) -> Optional[str]:
        """Helper to fetch and decode file content."""
        try:
            content_file = repo.get_contents(filepath)
            if isinstance(content_file, list):
                return None
            return base64.b64decode(content_file.content).decode('utf-8')
        except Exception:
            return None

    def _process_single_repo(self, repo) -> Repository:
        """
        Fetches all raw data for a single repository.
        Executed in parallel.
        """
        # 1. Fetch File Tree (Recursive)
        # Use get_git_tree to get the full tree. This allows deep mining for StructureCollector.
        file_tree = []
        try:
            # Get the SHA of the default branch
            branch = repo.get_branch(repo.default_branch)
            tree = repo.get_git_tree(branch.commit.sha, recursive=True)
            file_tree = [element.path for element in tree.tree]
        except Exception:
            # Fallback to root contents if tree fetch fails (e.g., empty repo or too large)
            try:
                contents = repo.get_contents("")
                file_tree = [c.name for c in contents]
            except Exception:
                pass

        # 2. Fetch Dependency Files
        # Check if the file exists in the tree (checking mostly for root existence or simple paths)
        target_files = [
            "requirements.txt", "package.json", "go.mod", "Cargo.toml", 
            "pom.xml", "pyproject.toml", "composer.json"
        ]
        dependency_files = {}
        for fname in target_files:
            # Check if the file exists in the fetched tree
            if fname in file_tree:
                content = self._fetch_content(repo, fname)
                if content:
                    dependency_files[fname] = content

        # 3. Fetch Repository README
        readme_content = None
        try:
            # get_readme() handles finding README.md, readme.txt, etc.
            readme = repo.get_readme()
            readme_content = base64.b64decode(readme.content).decode('utf-8')
        except Exception:
            pass

        # 4. Fetch Commit History (Last 15)
        commit_history = []
        try:
            commits = repo.get_commits()[:15]
            for commit in commits:
                commit_history.append({
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "date": commit.commit.author.date.isoformat(),
                    "author": commit.commit.author.name
                })
        except Exception:
            pass
        
        # 5. Fetch Topics
        topics = []
        try:
            topics = repo.get_topics()
        except Exception:
            pass

        return Repository(
            name=repo.name,
            description=repo.description,
            language=repo.language,
            stargazers_count=repo.stargazers_count,
            forks_count=repo.forks_count,
            updated_at=repo.updated_at.isoformat(),
            html_url=repo.html_url,
            has_ci=False,      # To be determined by analyzer
            has_docker=False,  # To be determined by analyzer
            has_tests=False,   # To be determined by analyzer
            has_license=False, # To be determined by analyzer
            dependencies=[],   # To be determined by analyzer
            topics=topics,
            file_tree=file_tree,
            dependency_files=dependency_files,
            readme_content=readme_content,
            commit_history=commit_history
        )

    def get_user_profile(self, username: str) -> UserProfile:
        try:
            user = self.client.get_user(username)
            
            # Fetch top 15 repositories
            # Sort by updated to get most relevant/active
            # Convert to list first (slicing)
            target_repos = list(user.get_repos(type='owner', sort='updated', direction='desc')[:15])
            
            # Parallel Fetching
            repositories_data = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_repo = {executor.submit(self._process_single_repo, repo): repo for repo in target_repos}
                for future in concurrent.futures.as_completed(future_to_repo):
                    try:
                        data = future.result()
                        if data:
                            repositories_data.append(data)
                    except Exception as exc:
                        repo = future_to_repo[future]
                        print(f"Repo {repo.name} generated an exception: {exc}")

            # Sort back by updated_at (parallel execution might scramble order)
            repositories_data.sort(key=lambda x: x.updated_at, reverse=True)

            # Fetch Profile README
            profile_readme = None
            try:
                profile_repo = user.get_repo(username)
                readme = profile_repo.get_readme()
                profile_readme = base64.b64decode(readme.content).decode('utf-8')
            except UnknownObjectException:
                pass
            except Exception:
                pass

            return UserProfile(
                username=user.login,
                name=user.name,
                bio=user.bio,
                location=user.location,
                public_repos=user.public_repos,
                followers=user.followers,
                following=user.following,
                avatar_url=user.avatar_url,
                html_url=user.html_url,
                readme_content=profile_readme,
                repositories=repositories_data
            )

        except UnknownObjectException:
            raise ValueError(f"GitHub user '{username}' not found.")
        except GithubException as e:
            raise ConnectionError(f"GitHub API error: {e.status} - {e.data.get('message', 'Unknown error')}")
        except Exception as e:
            raise ConnectionError(f"An unexpected error occurred: {str(e)}")
