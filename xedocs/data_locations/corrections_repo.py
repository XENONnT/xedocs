
from .github import GithubRepo


class CorrectionsRepo(GithubRepo):
    class Config:
        env_prefix = "XEDOCS_CORRECTIONS_REPO_"
    
    repo: str = "corrections"
