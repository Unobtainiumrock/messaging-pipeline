# CICD_SETUP.md

## Setting Up Your CI/CD Pipeline

This document provides step-by-step instructions for setting up and configuring your CI/CD pipeline using GitHub Actions and Repository Secrets.

### Table of Contents

1.  [Initial Setup](#initial-setup)
2.  [Configuring GitHub Secrets](#configuring-github-secrets)
3.  [Workflow Configuration](#workflow-configuration)
4.  [Deployment Setup](#deployment-setup)
5.  [Monitoring Integration](#monitoring-integration)
6.  [Troubleshooting](#troubleshooting)

## Initial Setup

1.  Ensure your repository has the following files:

    - `.github/workflows/main.yml` - Your CI/CD workflow (using the updated structure without Environments)
    - `scripts/deploy_to_ec2.sh` - Deployment script
    - `scripts/setup_monitoring.sh` - Monitoring configuration (if applicable)

2.  Make sure your scripts are executable:
    ```bash
    chmod +x scripts/deploy_to_ec2.sh scripts/setup_monitoring.sh
    ```

## Configuring GitHub Secrets

Since GitHub Environments features (like environment-specific secrets and protection rules) are not available on the Free plan for private repositories, all secrets must be configured as **Repository Secrets**.

1.  Navigate to your repository on GitHub.
2.  Go to **Settings → Secrets and variables → Actions → Secrets** tab.
3.  Add the following repository secrets:
    - `STAGING_EC2_IP`: IP address of your staging server.
    - `PRODUCTION_EC2_IP`: IP address of your production server.
    - `STAGING_SSH_PRIVATE_KEY`: SSH private key used for accessing the staging server.
    - `PRODUCTION_SSH_PRIVATE_KEY`: SSH private key used for accessing the production server.
    - `SNYK_TOKEN`: Your Snyk API token for vulnerability scanning.
    - `SLACK_WEBHOOK_URL`: The Slack Incoming Webhook URL for deployment notifications.
    - _(Add any other secrets your deployment or application scripts might need, e.g., `SLACK_API_KEY`, `DISCORD_API_KEY`, `GOOGLE_API_KEY` if used)_

## Workflow Configuration

Your `.github/workflows/main.yml` file should include jobs for:

1.  Testing and code quality checks (`test` job)
2.  Security scanning (`security-scan` job)
3.  Versioning (`version` job)
4.  Documentation generation (`docs` job)
5.  Building Docker images (`build` job)
6.  Deployment to staging (`deploy-staging` job, triggered by push to `develop`)
7.  Deployment to production (`deploy-production` job, triggered by push to `master` or manually via `workflow_dispatch` if you implemented that alternative)

Ensure your workflow deployment jobs reference the correct repository secrets and **do not** use the `environment:` key:

```yaml
# Example snippet for deploy-staging job
deploy-staging:
  if: github.ref == 'refs/heads/develop' # Or appropriate trigger
  needs: [build, version]
  runs-on: ubuntu-latest
  # NO 'environment:' key here
  steps:
    # ... checkout, download artifact steps ...

    - name: Set up SSH key
      uses: webfactory/ssh-agent@v0.7.0
      with:
        # Use the staging-specific SSH key from Repository Secrets
        ssh-private-key: ${{ secrets.STAGING_SSH_PRIVATE_KEY }}

    - name: Deploy to staging
      env:
        VERSION: ${{ needs.version.outputs.new_version || github.sha }}
        NOTIFICATION_WEBHOOK: ${{ secrets.SLACK_WEBHOOK_URL }}
      run: |
        # Use the staging IP from Repository Secrets
        ./scripts/deploy_to_ec2.sh ${{ secrets.STAGING_EC2_IP }} staging $VERSION
        # ... Slack notification ...
```

(Ensure the `deploy-production` job is similarly updated to use `secrets.PRODUCTION_SSH_PRIVATE_KEY` and `secrets.PRODUCTION_EC2_IP`)

## Deployment Setup

Configure your `scripts/deploy_to_ec2.sh` script to handle:

1. Accepting environment name (e.g., "staging", "production") and version as arguments.

2. Using the correct server IP passed as an argument.

3. Loading the Docker image from the `.tar` artifact (if not already done in the workflow).

4. Stopping the old container, pulling/starting the new one.

5. Performing necessary health checks.

6. Potentially handling rollbacks.

Example for storing application secrets (which should also be GitHub repository secrets) on deployment targets:

```bash
# Example within deploy_to_ec2.sh, using arguments $1=IP, $2=ENV_NAME, $3=VERSION
EC2_IP=$1
ENVIRONMENT=$2
# Assuming secrets like SLACK_API_KEY are passed via env vars to the script

# Create .env file on target server
ssh $SSH_OPTIONS ec2-user@<span class="math-inline">EC2\_IP << EOF
cd /app
\# Ensure sensitive values are handled carefully, ideally passed securely
\# or fetched from a secrets manager on the instance if possible\.
\# This example assumes they are passed as environment variables to the script\.
cat \> \.env << 'EOFINNER'
SLACK\_API\_KEY\=</span>{SLACK_API_KEY_SECRET}
DISCORD_API_KEY=<span class="math-inline">\{DISCORD\_API\_KEY\_SECRET\}
GOOGLE\_API\_KEY\=</span>{GOOGLE_API_KEY_SECRET}
ENVIRONMENT=${ENVIRONMENT}
EOFINNER
EOF
```

(Note: Passing secrets directly into the `.env` file via SSH like this requires careful handling. Ensure the environment variables `SLACK_API_KEY_SECRET` etc. are securely passed to the `deploy_to_ec2.sh` script if needed, likely sourced from GitHub repository secrets in the workflow file's `env:` block.)

## Monitoring Integration

Ensure your monitoring script (if used):

1. Can distinguish between staging and production environments (perhaps based on an argument or hostname).

2. Sets appropriate alarm thresholds.

3. Sends notifications to the right channels.

## Troubleshooting

Common issues:

1. **Workflow fails during SSH step:**

   - Check if the correct secret (`STAGING_SSH_PRIVATE_KEY` or `PRODUCTION_SSH_PRIVATE_KEY`) is populated in GitHub Repository Secrets and is correctly formatted.

   - Ensure the corresponding public key is added to the `authorized_keys` on the correct server (`STAGING_EC2_IP` or `PRODUCTION_EC2_IP`).

   - Verify network connectivity/firewall rules between GitHub Actions runners and your EC2 instances.

2. **Deployment succeeds but application doesn't work: **

   - Check if all required environment variables are set correctly on the target server (verify the process in `deploy_to_ec2.sh`).

   - Verify Docker container logs on the target server (`docker logs <container_name_or_id>`).

3. **Security scanning reports vulnerabilities:**

   - Review the security report (Trivy SARIF in GitHub Security tab, Snyk logs/dashboard).

   - Update dependencies or address the vulnerabilities.

   - Consider adding exceptions for false positives if applicable (e.g., `.snyk` policy file).

For more information, refer to:

- [GitHub Actions documentation](https://docs.github.com/en/actions)

- [GitHub Secrets management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

- [Snyk Stuff](https://docs.snyk.io/snyk-cli/using-the-snyk-cli/snyk-cli-for-github-actions)
