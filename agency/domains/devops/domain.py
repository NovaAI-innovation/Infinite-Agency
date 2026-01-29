from typing import Dict, Any
from ...core.base_domain import BaseDomain, DomainInput, DomainOutput
import json


class DevOpsDomain(BaseDomain):
    """Domain responsible for DevOps practices including CI/CD, infrastructure, and deployment"""

    def __init__(self, name: str = "devops", description: str = "Manages CI/CD pipelines, infrastructure as code, and deployment automation", resource_manager=None, cache_enabled: bool = True):
        super().__init__(name=name, description=description, resource_manager=resource_manager, cache_enabled=cache_enabled)
        self.ci_cd_platforms = ["github_actions", "jenkins", "gitlab_ci", "circleci", "travis_ci", "azure_devops"]
        self.infra_platforms = ["terraform", "cloudformation", "ansible", "puppet", "chef", "kubernetes"]
        self.container_platforms = ["docker", "podman", "containerd"]
        self.cloud_platforms = ["aws", "azure", "gcp", "digitalocean", "oci"]
        self.monitoring_tools = ["prometheus", "grafana", "datadog", "new_relic", "splunk", "elk"]
        self.devops_templates = {
            "ci_cd": self._generate_ci_cd_template,
            "infrastructure": self._generate_infrastructure_template,
            "containerization": self._generate_containerization_template,
            "monitoring": self._generate_monitoring_template,
            "deployment": self._generate_deployment_template
        }

    async def execute(self, input_data: DomainInput) -> DomainOutput:
        """Generate DevOps configurations based on the input specification"""
        try:
            # Acquire resources before executing
            if not await self.resource_manager.acquire_resources(self.name):
                return DomainOutput(
                    success=False,
                    error=f"Resource limits exceeded for domain {self.name}"
                )

            try:
                query = input_data.query.lower()
                context = input_data.context
                params = input_data.parameters

                # Determine the type of DevOps configuration to generate
                devops_type = self._determine_devops_type(query)
                ci_cd_platform = params.get("ci_cd_platform", context.get("ci_cd_platform", "github_actions"))
                infra_platform = params.get("infra_platform", context.get("infra_platform", "terraform"))
                cloud_platform = params.get("cloud_platform", context.get("cloud_platform", "aws"))

                if ci_cd_platform not in self.ci_cd_platforms:
                    return DomainOutput(
                        success=False,
                        error=f"CI/CD platform '{ci_cd_platform}' not supported. Available platforms: {', '.join(self.ci_cd_platforms)}"
                    )

                # Generate the DevOps configuration
                generated_config = self._generate_devops_config(devops_type, query, ci_cd_platform, infra_platform, cloud_platform, params)

                # Enhance the configuration if other domains are available
                enhanced_config = await self._enhance_with_other_domains(generated_config, input_data)

                return DomainOutput(
                    success=True,
                    data={
                        "configuration": enhanced_config,
                        "type": devops_type,
                        "ci_cd_platform": ci_cd_platform,
                        "infra_platform": infra_platform,
                        "cloud_platform": cloud_platform,
                        "original_query": query
                    },
                    metadata={
                        "domain": self.name,
                        "enhanced": enhanced_config != generated_config
                    }
                )
            finally:
                # Always release resources after execution
                self.resource_manager.release_resources(self.name)
        except Exception as e:
            return DomainOutput(
                success=False,
                error=f"DevOps configuration generation failed: {str(e)}"
            )

    def can_handle(self, input_data: DomainInput) -> bool:
        """Determine if this domain can handle the input"""
        query = input_data.query.lower()

        # Check for keywords that suggest DevOps configuration
        devops_keywords = [
            "ci/cd", "continuous integration", "continuous deployment", "pipeline", 
            "jenkins", "github actions", "gitlab ci", "circleci", "travis", 
            "infrastructure as code", "terraform", "ansible", "cloudformation", 
            "docker", "kubernetes", "container", "deployment", "devops", 
            "automated deployment", "iac", "infrastructure automation", 
            "monitoring", "observability", "logging", "alerting", 
            "scaling", "load balancing", "auto scaling", "blue green deployment"
        ]

        return any(keyword in query for keyword in devops_keywords)

    def _determine_devops_type(self, query: str) -> str:
        """Determine what type of DevOps configuration to generate based on the query"""
        if any(word in query for word in ["ci", "cd", "pipeline", "continuous integration", "continuous deployment"]):
            return "ci_cd"
        elif any(word in query for word in ["infrastructure", "iac", "terraform", "ansible", "cloudformation"]):
            return "infrastructure"
        elif any(word in query for word in ["docker", "container", "kubernetes", "podman"]):
            return "containerization"
        elif any(word in query for word in ["monitoring", "observability", "logging", "metrics", "alerting"]):
            return "monitoring"
        elif any(word in query for word in ["deployment", "deploy", "release", "production"]):
            return "deployment"
        else:
            return "ci_cd"  # Default to CI/CD

    def _generate_devops_config(self, devops_type: str, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate DevOps configuration based on type, query, and platforms"""
        if devops_type in self.devops_templates:
            return self.devops_templates[devops_type](query, ci_cd_platform, infra_platform, cloud_platform, params)
        else:
            return self._generate_generic_devops_config(query, devops_type, ci_cd_platform, infra_platform, cloud_platform, params)

    def _generate_ci_cd_template(self, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate a CI/CD pipeline template based on the query"""
        if ci_cd_platform == "github_actions":
            return f"""# GitHub Actions CI/CD Pipeline for {query}

name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{{{ matrix.python-version }}}}
      uses: actions/setup-python@v3
      with:
        python-version: ${{{{ matrix.python-version }}}}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Run linting
      run: |
        python -m flake8 .
    
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build and push Docker image
      run: |
        docker build -t myapp:${{{{ github.sha }}}}.
        docker push myapp:${{{{ github.sha }}}}.
    
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - name: Deploy to {cloud_platform}
      run: |
        # Deployment commands for {cloud_platform}
        echo "Deploying to {cloud_platform}"
"""
        elif ci_cd_platform == "jenkins":
            return f"""# Jenkinsfile for {query}

pipeline {{
    agent any

    tools {{
        maven 'Maven 3.8.1'
        jdk 'OpenJDK 11'
    }}

    stages {{
        stage('Checkout') {{
            steps {{
                checkout scm
            }}
        }}

        stage('Build') {{
            steps {{
                sh 'mvn clean compile'
            }}
        }}

        stage('Test') {{
            steps {{
                sh 'mvn test'
            }}
            post {{
                always {{
                    publishTestResults testResultsPattern: 'target/surefire-reports/*.xml'
                }}
            }}
        }}

        stage('Package') {{
            steps {{
                sh 'mvn package'
            }}
        }}

        stage('Deploy') {{
            when {{
                branch 'main'
            }}
            steps {{
                script {{
                    // Deploy to {cloud_platform}
                    sh "echo 'Deploying to {cloud_platform}'"
                }}
            }}
        }}
    }}

    post {{
        always {{
            archiveArtifacts artifacts: 'target/*.jar', fingerprint: true
        }}
        success {{
            echo 'Pipeline completed successfully!'
        }}
        failure {{
            echo 'Pipeline failed!'
        }}
    }}
}}
"""
        else:
            return f"# CI/CD Pipeline for {query} on {ci_cd_platform}"

    def _generate_infrastructure_template(self, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate infrastructure as code template based on the query"""
        if infra_platform == "terraform":
            return f"""# Terraform Infrastructure for {query}

# Provider configuration
provider "aws" {{
  region = var.aws_region
}}

# VPC
resource "aws_vpc" "{query.replace(' ', '_')}_vpc" {{
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "{query.replace(' ', '_')}-vpc"
  }}
}}

# Internet Gateway
resource "aws_internet_gateway" "{query.replace(' ', '_')}_igw" {{
  vpc_id = aws_vpc.{query.replace(' ', '_')}_vpc.id

  tags = {{
    Name = "{query.replace(' ', '_')}-igw"
  }}
}}

# Subnets
resource "aws_subnet" "{query.replace(' ', '_')}_public_subnet" {{
  count                   = 2
  vpc_id                  = aws_vpc.{query.replace(' ', '_')}_vpc.id
  cidr_block              = "10.0.${{count.index + 1}}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {{
    Name = "{query.replace(' ', '_')}-public-${{count.index}}"
  }}
}}

# Security Groups
resource "aws_security_group" "{query.replace(' ', '_')}_web_sg" {{
  name_prefix = "{query.replace(' ', '_')}-web-sg"
  vpc_id      = aws_vpc.{query.replace(' ', '_')}_vpc.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# EC2 Instance
resource "aws_instance" "{query.replace(' ', '_')}_instance" {{
  ami                         = data.aws_ami.latest_amazon_linux.id
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.{query.replace(' ', '_')}_public_subnet[0].id
  vpc_security_group_ids      = [aws_security_group.{query.replace(' ', '_')}_web_sg.id]
  associate_public_ip_address = true

  tags = {{
    Name = "{query.replace(' ', '_')}-instance"
  }}
}}

# Outputs
output "instance_public_ip" {{
  value = aws_instance.{query.replace(' ', '_')}_instance.public_ip
}}

output "vpc_id" {{
  value = aws_vpc.{query.replace(' ', '_')}_vpc.id
}}

# Variables
variable "aws_region" {{
  description = "AWS region"
  default     = "{cloud_platform}"
}}

# Data sources
data "aws_ami" "latest_amazon_linux" {{
  most_recent = true
  owners      = ["amazon"]

  filter {{
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }}
}}

data "aws_availability_zones" "available" {{
  state = "available"
}}
"""
        elif infra_platform == "ansible":
            return f"""# Ansible Playbook for {query}

---
- name: Deploy {query} infrastructure
  hosts: localhost
  gather_facts: no
  vars:
    aws_region: {cloud_platform}
    instance_type: t3.micro
    ami_id: ami-0abcdef1234567890  # Replace with actual AMI ID

  tasks:
    - name: Create VPC
      amazon.aws.ec2_vpc_net:
        name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}_vpc"
        cidr_block: 10.0.0.0/16
        region: "{{ '{{' }} aws_region {{ '}}' }}"
        tags:
          Name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-vpc"
      register: vpc

    - name: Create Internet Gateway
      amazon.aws.ec2_vpc_igw:
        vpc_id: "{{ '{{' }} vpc.vpc.id {{ '}}' }}"
        region: "{{ '{{' }} aws_region {{ '}}' }}"
        tags:
          Name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-igw"

    - name: Create Subnet
      amazon.aws.ec2_vpc_subnet:
        vpc_id: "{{ '{{' }} vpc.vpc.id {{ '}}' }}"
        cidr: 10.0.1.0/24
        az: "{{ '{{' }} aws_region {{ '}}' }}a"
        region: "{{ '{{' }} aws_region {{ '}}' }}"
        tags:
          Name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-subnet"

    - name: Create Security Group
      amazon.aws.ec2_security_group:
        name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-web-sg"
        description: Security group for web servers
        vpc_id: "{{ '{{' }} vpc.vpc.id {{ '}}' }}"
        region: "{{ '{{' }} aws_region {{ '}}' }}"
        rules:
          - proto: tcp
            ports:
              - 80
            cidr_ip: 0.0.0.0/0
            rule_desc: HTTP access
          - proto: tcp
            ports:
              - 443
            cidr_ip: 0.0.0.0/0
            rule_desc: HTTPS access
        tags:
          Name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-web-sg"

    - name: Launch EC2 Instance
      amazon.aws.ec2_instance:
        name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-instance"
        image_id: "{{ '{{' }} ami_id {{ '}}' }}"
        instance_type: "{{ '{{' }} instance_type {{ '}}' }}"
        vpc_subnet_id: "{{ '{{' }} vpc.vpc.subnet_set[0].id {{ '}}' }}"
        security_groups:
          - "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-web-sg"
        region: "{{ '{{' }} aws_region {{ '}}' }}"
        wait: yes
        tags:
          Name: "{{ '{{' }} query.replace(' ', '_') {{ '}}' }}-instance"
      register: ec2_instance

    - name: Display instance information
      ansible.builtin.debug:
        msg: "Instance launched with IP: {{ '{{' }} ec2_instance.instances[0].public_ip_address {{ '}}' }}"
"""
        else:
            return f"# Infrastructure as Code for {query} using {infra_platform}"

    def _generate_containerization_template(self, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate containerization configuration based on the query"""
        return f"""# Containerization for {query}

## Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]

## docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - .:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:

## Kubernetes Deployment (using {cloud_platform})
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {query.replace(' ', '-')}-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {query.replace(' ', '-')}-app
  template:
    metadata:
      labels:
        app: {query.replace(' ', '-')}-app
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENV
          value: "production"
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"

---
apiVersion: v1
kind: Service
metadata:
  name: {query.replace(' ', '-')}-service
spec:
  selector:
    app: {query.replace(' ', '-')}-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
"""

    def _generate_monitoring_template(self, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate monitoring configuration based on the query"""
        return f"""# Monitoring for {query}

## Prometheus Configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'app'
    static_configs:
      - targets: ['app:8000']

## Grafana Dashboard Configuration
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards

## Alertmanager Configuration
route:
  receiver: 'default-receiver'
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h

receivers:
  - name: 'default-receiver'
    webhook_configs:
      - url: 'http://alert-webhook:3000/webhook'

## Application Metrics Endpoint
# Add to your application code:
from prometheus_client import Counter, Histogram, start_http_server
import time

REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_TIME = Histogram('app_request_duration_seconds', 'Request duration')

def monitor_request(method, endpoint):
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
    REQUEST_TIME.time()

## Logging Configuration
version: '3.8'

services:
  app:
    # ... app configuration ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
"""

    def _generate_deployment_template(self, query: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate deployment configuration based on the query"""
        return f"""# Deployment Configuration for {query}

## Blue-Green Deployment Strategy

### AWS ECS Deployment
AWSTemplateFormatVersion: '2010-09-09'
Description: Blue-Green Deployment for {query}

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [staging, production]

Resources:
  # Task Definition
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: {query.replace(' ', '-')}-task
      NetworkMode: awsvpc
      RequiresCompatibilities:
        - FARGATE
      Cpu: 256
      Memory: 512
      ExecutionRoleArn: !GetAtt ExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: app
          Image: !Sub '${{AWS::AccountId}}.dkr.ecr.${{AWS::Region}}.amazonaws.com/{query.replace(' ', '-')}:latest'
          PortMappings:
            - ContainerPort: 8000
              Protocol: tcp
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: ecs

  # Service
  Service:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: {query.replace(' ', '-')}-service
      Cluster: !Ref Cluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: 2
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref Subnets
          SecurityGroups:
            - !Ref SecurityGroup
          AssignPublicIp: ENABLED

### Kubernetes Deployment with Rollout Strategy
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: {query.replace(' ', '-')}-rollout
spec:
  replicas: 3
  strategy:
    blueGreen:
      activeService: {query.replace(' ', '-')}-service-active
      previewService: {query.replace(' ', '-')}-service-preview
      autoPromotionEnabled: false
      scaleDownDelaySeconds: 30
      prePromotionAnalysis:
        templates:
        - templateName: {query.replace(' ', '-')}-success-rate
        args:
        - name: service-name
          value: {query.replace(' ', '-')}-service-preview
      postPromotionAnalysis:
        templates:
        - templateName: {query.replace(' ', '-')}-success-rate
        args:
        - name: service-name
          value: {query.replace(' ', '-')}-service-active
  selector:
    matchLabels:
      app: {query.replace(' ', '-')}-app
  template:
    metadata:
      labels:
        app: {query.replace(' ', '-')}-app
    spec:
      containers:
      - name: app
        image: myapp:latest
        ports:
        - containerPort: 8000

## Deployment Scripts
#!/bin/bash
# deploy.sh

ENVIRONMENT=${{1:-staging}}
IMAGE_TAG=${{2:-latest}}

echo "Deploying {query} to $ENVIRONMENT environment with image tag $IMAGE_TAG"

# Update Kubernetes deployment
kubectl set image deployment/{query.replace(' ', '-')}-app app=myapp:$IMAGE_TAG --namespace=$ENVIRONMENT

# Wait for rollout to complete
kubectl rollout status deployment/{query.replace(' ', '-')}-app --namespace=$ENVIRONMENT

# Verify deployment
kubectl get pods --namespace=$ENVIRONMENT
"""

    def _generate_generic_devops_config(self, query: str, devops_type: str, ci_cd_platform: str, infra_platform: str, cloud_platform: str, params: Dict[str, Any]) -> str:
        """Generate generic DevOps configuration when specific type isn't determined"""
        return f"""# DevOps Configuration

## Overview
This document outlines the DevOps configuration for {query}.

## Components
- CI/CD Pipeline: {ci_cd_platform}
- Infrastructure: {infra_platform}
- Cloud Platform: {cloud_platform}
- Type: {devops_type}

## Configuration Details
TODO: Add specific configuration details for the {devops_type} setup.
"""

    async def _enhance_with_other_domains(self, generated_config: str, input_data: DomainInput) -> str:
        """Allow other domains to enhance the generated DevOps configuration"""
        # In a real implementation, this would coordinate with other domains
        # For now, we'll just return the original configuration
        return generated_config