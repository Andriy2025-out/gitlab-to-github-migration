import os
import subprocess
import shutil
import requests
import time
import logging

# Load GitLab & GitHub Tokens from Environment Variables
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# GitHub Username or Org (Change this)
GITHUB_USERNAME = "Andriy2025-out"

# GitHub API URL
GITHUB_API_URL = "https://api.github.com"

# Setup Logging
LOG_FILE = "migration.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)


def run_command(command):
    """Executes shell commands and logs output."""
    logging.info(f"Running command: {command}")
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        logging.info(f"✅ Command succeeded: {command}")
        logging.debug(f"Output:\n{process.stdout.strip()}")
    else:
        logging.error(f"❌ Command failed: {command}")
        logging.error(f"Error:\n{process.stderr.strip()}")

    return process.returncode


def github_repo_exists(repo_name):
    """Checks if the GitHub repository already exists."""
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        logging.info(f"🔹 GitHub repository '{repo_name}' already exists.")
        return True
    elif response.status_code == 404:
        logging.info(f"🆕 GitHub repository '{repo_name}' does not exist, creating it.")
        return False
    else:
        logging.error(f"❌ Error checking GitHub repository: {response.text}")
        return False


def is_gitlab_repo_private(gitlab_repo):
    """Check if a GitLab repository is private."""
    headers = {"Private-Token": GITLAB_TOKEN}
    repo_path = gitlab_repo.replace("https://gitlab.com/", "").replace(".git", "")
    url = f"https://gitlab.com/api/v4/projects/{requests.utils.quote(repo_path, safe='')}"

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        visibility = response.json().get("visibility", "private")
        is_private = visibility != "public"  # True if private, False if public
        logging.info(f"🔍 GitLab repo '{repo_path}' is {'Private' if is_private else 'Public'}")
        return is_private
    else:
        logging.error(f"❌ Failed to check GitLab repository visibility: {response.text}")
        return True  # Default to private if check fails


def create_github_repo(repo_name, gitlab_repo):
    """Creates a new repository on GitHub with the same visibility as GitLab."""
    is_private = is_gitlab_repo_private(gitlab_repo)

    if github_repo_exists(repo_name):
        return True

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": is_private,  # Set the correct visibility
        "description": f"Migrated from GitLab: {repo_name}"
    }

    response = requests.post(f"{GITHUB_API_URL}/user/repos", json=data, headers=headers)

    if response.status_code == 201:
        logging.info(f"✅ Created GitHub repository '{repo_name}' (Private: {is_private}).")
        return True
    else:
        logging.error(f"❌ Failed to create GitHub repo '{repo_name}': {response.text}")
        return False


def migrate_repo(gitlab_repo):
    """Migrates a single repository from GitLab to GitHub."""
    repo_name = gitlab_repo.split("/")[-1].replace(".git", "")
    github_repo = f"https://github.com/{GITHUB_USERNAME}/{repo_name}.git"

    gitlab_auth_url = gitlab_repo.replace("https://", f"https://oauth2:{GITLAB_TOKEN}@")
    github_auth_url = github_repo.replace("https://", f"https://{GITHUB_TOKEN}@")

    logging.info(f"🚀 Starting migration for {repo_name}...")

    try:
        # Step 1: Create GitHub Repository if it doesn't exist
        if not create_github_repo(repo_name, gitlab_repo):
            logging.error(f"Skipping {repo_name}: GitHub repo creation failed.")
            return

        # Step 2: Remove existing repo folder (if exists)
        if os.path.exists(repo_name):
            shutil.rmtree(repo_name)
            logging.info(f"🗑️ Removed existing directory: {repo_name}")

        # Step 3: Clone the GitLab repository (mirror mode)
        logging.info(f"🔄 Cloning {gitlab_repo}...")
        if run_command(f"git clone --mirror {gitlab_auth_url} {repo_name}") != 0:
            logging.error(f"🚨 Cloning failed for {repo_name}. Skipping.")
            return

        os.chdir(repo_name)

        # Step 4: Add GitHub as a new remote
        logging.info(f"🔄 Adding GitHub remote for {repo_name}...")
        if run_command(f"git remote add github {github_auth_url}") != 0:
            logging.error(f"🚨 Failed to add remote for {repo_name}. Skipping.")
            os.chdir("..")
            return

        # Step 5: Push all branches and tags to GitHub
        logging.info(f"🚀 Pushing {repo_name} to GitHub...")
        if run_command("git push --mirror github") != 0:
            logging.error(f"🚨 Failed to push {repo_name} to GitHub. Skipping.")
            os.chdir("..")
            return

        logging.info(f"✅ Successfully migrated {repo_name}!")

    except Exception as e:
        logging.exception(f"🚨 Unexpected error during migration of {repo_name}: {str(e)}")

    finally:
        # Step 6: Cleanup
        os.chdir("..")
        shutil.rmtree(repo_name, ignore_errors=True)
        logging.info(f"🧹 Cleaned up local repository: {repo_name}")


if __name__ == "__main__":
    logging.info("🚀 Starting bulk repository migration...")

    if os.path.exists("repos.txt"):
        with open("repos.txt", "r") as f:
            repo_list = [line.strip() for line in f.readlines() if line.strip()]
    else:
        logging.error("❌ Error: repos.txt file not found.")
        exit(1)

    for gitlab_repo in repo_list:
        migrate_repo(gitlab_repo)
        time.sleep(2)  # Small delay to avoid GitHub rate limits

    logging.info("🎉 Bulk migration completed! Check migration.log for details.")
