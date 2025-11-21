import os
from github import Github, GithubException, UnknownObjectException
from app.core.interfaces import IGithubProvider
from app.models.dtos import UserProfile, Repository
from app.services.collectors import StructureCollector, DependencyCollector
from typing import Optional, List
import base64

class GithubProvider(IGithubProvider):
    """
    Concrete implementation of IGithubProvider using PyGithub.
    """
    
    def __init__(self, token: Optional[str] = None):
        # Initialize PyGithub with a token (optional but recommended)
        # If no token is provided, it uses unauthenticated requests (lower rate limits)
        self.client = Github(token)
        self.structure_collector = StructureCollector()
        self.dependency_collector = DependencyCollector()

    def fetch_file_content(self, repo, filepath: str) -> Optional[str]:
        """
        Fetches the raw string content of a file from the repository.
        Returns None if the file does not exist.
        """
        try:
            content_file = repo.get_contents(filepath)
            # content_file can be a list if filepath is a directory, handle that
            if isinstance(content_file, list):
                return None
            return base64.b64decode(content_file.content).decode('utf-8')
        except UnknownObjectException:
            return None
        except Exception as e:
            # print(f"Error fetching {filepath} from {repo.name}: {e}")
            return None

    def fetch_repo_structure(self, repo) -> List[str]:
        """
        Returns a simplified list of root files/folders in the repository.
        """
        try:
            contents = repo.get_contents("")
            return [c.name for c in contents]
        except Exception as e:
            # print(f"Error fetching structure for {repo.name}: {e}")
            return []

    def get_user_profile(self, username: str) -> UserProfile:
        try:
            user = self.client.get_user(username)
            
            # Fetch Repositories
            repos_data = []
            # We explicitly fetch non-forked repos or all, depending on logic.
            # For simplicity, we fetch public repos.
            for repo in user.get_repos(type='owner', sort='updated', direction='desc'):
                # Limit to top 10 to balance depth of analysis with rate limits
                if len(repos_data) >= 10:
                    break
                
                # 1. Fetch Structure & Analyze Flags
                structure = self.fetch_repo_structure(repo)
                flags = self.structure_collector.analyze(structure)
                
                # 2. Fetch Dependencies
                dependencies = self.dependency_collector.analyze(repo, self.fetch_file_content)

                repos_data.append(Repository(
                    name=repo.name,
                    description=repo.description,
                    language=repo.language,
                    stargazers_count=repo.stargazers_count,
                    forks_count=repo.forks_count,
                    updated_at=repo.updated_at.isoformat(),
                    html_url=repo.html_url,
                    has_ci=flags['has_ci'],
                    has_docker=flags['has_docker'],
                    has_tests=flags['has_tests'],
                    has_license=flags['has_license'],
                    dependencies=dependencies
                ))

            # Fetch Profile README
            readme_content = None
            try:
                # Try to find a repo with the same name as the user (special profile repo)
                profile_repo = user.get_repo(username)
                readme = profile_repo.get_readme()
                readme_content = base64.b64decode(readme.content).decode('utf-8')
            except UnknownObjectException:
                # Profile README doesn't exist
                pass
            except Exception as e:
                # Log warning ideally
                print(f"Warning: Could not fetch README for {username}: {e}")

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
                readme_content=readme_content,
                repositories=repos_data
            )

        except UnknownObjectException:
            raise ValueError(f"GitHub user '{username}' not found.")
        except GithubException as e:
            raise ConnectionError(f"GitHub API error: {e.status} - {e.data.get('message', 'Unknown error')}")
        except Exception as e:
            raise ConnectionError(f"An unexpected error occurred: {str(e)}")