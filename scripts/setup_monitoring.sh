#!/bin/bash
# Enhanced monitoring setup with CI/CD integration

ENVIRONMENT=$1
VERSION=$2

# Set up CloudWatch alarms for deployment monitoring
setup_deployment_monitoring() {
  local env=$1
  local version=$2

  # Create custom metrics namespace for deployments
  aws cloudwatch put-metric-data \
    --namespace "MyApp/Deployments" \
    --metric-name "Deployment" \
    --dimensions "Environment=$env,Version=$version" \
    --value 1

  # Set up alarms for application health
  aws cloudwatch put-metric-alarm \
    --alarm-name "$env-app-health" \
    --alarm-description "Alarm for $env application health" \
    --metric-name "HealthCheck" \
    --namespace "MyApp/Health" \
    --statistic "Average" \
    --period 60 \
    --threshold 1 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 3 \
    --alarm-actions "$SNS_TOPIC_ARN" \
    --dimensions "Environment=$env,Version=$version"
}

# Set up log monitoring for deployment events
setup_log_monitoring() {
  local env=$1

  aws logs create-log-group --log-group-name "/myapp/$env/deployments"

  # Create metric filter for failed deployments
  aws logs put-metric-filter \
    --log-group-name "/myapp/$env/deployments" \
    --filter-name "FailedDeployments" \
    --filter-pattern "FAILED" \
    --metric-transformations \
        metricName=DeploymentFailures,metricNamespace=MyApp/Deployments,metricValue=1
}

# Initialize monitors based on environment
setup_deployment_monitoring $ENVIRONMENT $VERSION
setup_log_monitoring $ENVIRONMENT

echo "Monitoring configured for $ENVIRONMENT deployment of version $VERSION"
