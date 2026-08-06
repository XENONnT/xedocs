# =====================================================================
# DEPRECATED: Leftover from the xeauth package.
# Disabled while severing the API dependency. 
# TODO: Remove completely in a future cleanup.
# =====================================================================
from .github import GithubRepo


class CorrectionsRepo(GithubRepo):
    class Config:
        env_prefix = "XEDOCS_CORRECTIONS_REPO_"
    
    repo: str = "corrections"
