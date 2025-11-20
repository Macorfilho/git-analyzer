import os
from github import Github, GithubException, UnknownObjectException
from app.core.interfaces import IGithubProvider
from app.models.dtos import UserProfile, Repository
from typing import Optional
import base64

class GithubProvider(IGithubProvider):
    """
    Concrete implementation of IGithubProvider using PyGithub.
    """
    
    def __init__(self, token: Optional[str] = None):
        # Initialize PyGithub with a token (optional but recommended)
        # If no token is provided, it uses unauthenticated requests (lower rate limits)
        self.client = Github(token)

    def get_user_profile(self, username: str) -> UserProfile:
        try:
            user = self.client.get_user(username)
            
            # Fetch Repositories
            # We explicitly fetch non-forked repos or all, depending on logic. 
            # For simplicity, we fetch public repos.
            repos_data = []
            for repo in user.get_repos(type='owner', sort='updated', direction='desc'):
                # Limit to last 20 to avoid excessive processing for now
                if len(repos_data) >= 20:
                    break
                    
                repos_data.append(Repository(
                    name=repo.name,
                    description=repo.description,
                    language=repo.language,
                    stargazers_count=repo.stargazers_count,
                    forks_count=repo.forks_count,
                    updated_at=repo.updated_at.isoformat(),
                    html_url=repo.html_url
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
