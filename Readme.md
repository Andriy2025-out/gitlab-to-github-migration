GitLab to GitHub Repository Migration Script

Overview

This script automates the migration of repositories from GitLab to GitHub, preserving all branches, commits, tags, and repository settings (public/private visibility). It supports bulk migration using a list of repositories.

Features

✅ Migrates repositories while keeping full commit history.
✅ Automatically creates repositories on GitHub with the correct public/private visibility.
✅ Supports bulk migration from a repos.txt file.
✅ Logs the entire process for easy troubleshooting (migration.log).
✅ Cleans up temporary files after migration.

Prerequisites

Before running the script, ensure you have:

Python 3+ installed.

A GitLab personal access token (PAT) with read_repository scope.

A GitHub personal access token (PAT) with repo scope.

Git installed on your machine.

Setup Instructions

1️⃣ Clone the Repository

git clone https://github.com/Andriy2025-out/gitlab-to-github-migration.git
cd gitlab-to-github-migration

2️⃣ Set Up Environment Variables

Store your GitLab and GitHub Personal Access Tokens (PATs) as environment variables:

export GITLAB_TOKEN="your_gitlab_personal_access_token"
export GITHUB_TOKEN="your_github_personal_access_token"

3️⃣ Create repos.txt

List the GitLab repositories you want to migrate in repos.txt (one per line):

https://gitlab.com/group/repository1.git
https://gitlab.com/group/repository2.git

4️⃣ Run the Migration Script

Execute the script:

python migrate_repos.py

5️⃣ Check Logs

View migration.log to debug or verify the migration process:

cat migration.log

Troubleshooting

❌ GitHub repositories are created as private instead of public

By default, the script preserves the public/private status of GitLab repositories. If a migrated repository is mistakenly private, ensure your GitLab token has sufficient permissions to read visibility settings.

❌ Git push failed

Ensure your GitHub token has repo permissions.

Check if your repository already exists on GitHub.

License

This script is open-source and available under the MIT License.

Contributing

Feel free to submit issues or pull requests to improve this script! 🚀

