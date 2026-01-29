from typing import Dict, Any, Optional, List
import asyncio
import subprocess
import json
import os
from pathlib import Path
import shutil
from dataclasses import dataclass
from enum import Enum
from ..utils.logger import get_logger


class DeploymentTarget(Enum):
    """Types of deployment targets"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    CUSTOM = "custom"


@dataclass
class DeploymentConfig:
    """Configuration for a deployment"""
    target: DeploymentTarget
    environment: str  # dev, staging, prod
    version: str
    replicas: int = 1
    resources: Dict[str, Any] = None  # CPU, memory, etc.
    environment_vars: Dict[str, str] = None
    ports: List[int] = None
    volumes: List[str] = None
    dependencies: List[str] = None
    health_check_path: str = "/health"
    readiness_check_path: str = "/ready"


class DeploymentManager:
    """Manages deployment of the agency system to various targets"""
    
    def __init__(self):
        self._logger = get_logger(__name__)
        self.deployment_configs: Dict[str, DeploymentConfig] = {}
    
    def register_deployment_config(self, name: str, config: DeploymentConfig):
        """Register a deployment configuration"""
        self.deployment_configs[name] = config
        self._logger.info(f"Registered deployment config: {name} for target {config.target.value}")
    
    async def deploy(self, config_name: str) -> bool:
        """Deploy using the specified configuration"""
        if config_name not in self.deployment_configs:
            self._logger.error(f"Deployment config '{config_name}' not found")
            return False
        
        config = self.deployment_configs[config_name]
        self._logger.info(f"Starting deployment to {config.target.value} environment: {config.environment}")
        
        try:
            if config.target == DeploymentTarget.LOCAL:
                success = await self._deploy_local(config)
            elif config.target == DeploymentTarget.DOCKER:
                success = await self._deploy_docker(config)
            elif config.target == DeploymentTarget.KUBERNETES:
                success = await self._deploy_kubernetes(config)
            elif config.target == DeploymentTarget.AWS:
                success = await self._deploy_aws(config)
            elif config.target == DeploymentTarget.AZURE:
                success = await self._deploy_azure(config)
            elif config.target == DeploymentTarget.GCP:
                success = await self._deploy_gcp(config)
            elif config.target == DeploymentTarget.CUSTOM:
                success = await self._deploy_custom(config)
            else:
                self._logger.error(f"Unsupported deployment target: {config.target}")
                return False
            
            if success:
                self._logger.info(f"Deployment to {config.target.value} completed successfully")
            else:
                self._logger.error(f"Deployment to {config.target.value} failed")
            
            return success
        except Exception as e:
            self._logger.error(f"Deployment failed with error: {e}")
            return False
    
    async def _deploy_local(self, config: DeploymentConfig) -> bool:
        """Deploy to local environment"""
        self._logger.info("Deploying to local environment")
        
        # For local deployment, we just need to start the service
        # This could involve starting a local server or running in a subprocess
        try:
            # Create a deployment directory
            deploy_dir = Path(f"deployments/local/{config.environment}")
            deploy_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy necessary files
            shutil.copytree("agency", deploy_dir / "agency", dirs_exist_ok=True)
            if Path("requirements.txt").exists():
                shutil.copy("requirements.txt", deploy_dir / "requirements.txt")
            
            # Write deployment info
            deployment_info = {
                "version": config.version,
                "environment": config.environment,
                "timestamp": asyncio.get_event_loop().time(),
                "config": config.__dict__
            }
            
            with open(deploy_dir / "deployment.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            self._logger.info(f"Local deployment created at {deploy_dir}")
            return True
        except Exception as e:
            self._logger.error(f"Local deployment failed: {e}")
            return False
    
    async def _deploy_docker(self, config: DeploymentConfig) -> bool:
        """Deploy using Docker"""
        self._logger.info("Deploying with Docker")
        
        try:
            # Check if Docker is available
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                self._logger.error("Docker is not available")
                return False
            
            # Create Dockerfile if it doesn't exist
            dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE {' '.join(map(str, config.ports or [8000]))}

CMD ["python", "-m", "agency.server"]
"""
            
            with open("Dockerfile", "w") as f:
                f.write(dockerfile_content)
            
            # Build the Docker image
            image_name = f"agency-{config.environment}:{config.version}"
            build_cmd = ["docker", "build", "-t", image_name, "."]
            result = subprocess.run(build_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"Docker build failed: {result.stderr}")
                return False
            
            # Run the container
            run_cmd = ["docker", "run", "-d"]
            
            # Add environment variables
            for key, value in (config.environment_vars or {}).items():
                run_cmd.extend(["-e", f"{key}={value}"])
            
            # Add port mappings
            for port in config.ports or [8000]:
                run_cmd.extend(["-p", f"{port}:{port}"])
            
            # Add volumes
            for volume in config.volumes or []:
                run_cmd.extend(["-v", volume])
            
            # Add resource limits
            if config.resources:
                if "memory" in config.resources:
                    run_cmd.extend(["--memory", str(config.resources["memory"])])
                if "cpus" in config.resources:
                    run_cmd.extend(["--cpus", str(config.resources["cpus"])])
            
            run_cmd.append(image_name)
            
            result = subprocess.run(run_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"Docker run failed: {result.stderr}")
                return False
            
            container_id = result.stdout.strip()
            self._logger.info(f"Docker container started: {container_id}")
            
            return True
        except Exception as e:
            self._logger.error(f"Docker deployment failed: {e}")
            return False
    
    async def _deploy_kubernetes(self, config: DeploymentConfig) -> bool:
        """Deploy to Kubernetes"""
        self._logger.info("Deploying to Kubernetes")
        
        try:
            # Check if kubectl is available
            result = subprocess.run(["kubectl", "version", "--client"], capture_output=True, text=True)
            if result.returncode != 0:
                self._logger.error("kubectl is not available")
                return False
            
            # Create Kubernetes manifest
            manifest = self._create_k8s_manifest(config)
            
            manifest_file = f"agency-{config.environment}.yaml"
            with open(manifest_file, "w") as f:
                f.write(manifest)
            
            # Apply the manifest
            apply_cmd = ["kubectl", "apply", "-f", manifest_file]
            result = subprocess.run(apply_cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self._logger.error(f"Kubernetes apply failed: {result.stderr}")
                return False
            
            self._logger.info("Kubernetes deployment applied successfully")
            return True
        except Exception as e:
            self._logger.error(f"Kubernetes deployment failed: {e}")
            return False
    
    def _create_k8s_manifest(self, config: DeploymentConfig) -> str:
        """Create Kubernetes manifest for the deployment"""
        env_vars = []
        for key, value in (config.environment_vars or {}).items():
            env_vars.append(f"            - name: {key}")
            env_vars.append(f"              value: '{value}'")
        
        env_section = "\n".join(env_vars) if env_vars else "            # No environment variables"
        
        ports = []
        for port in config.ports or [8000]:
            ports.append(f"          - containerPort: {port}")
        
        ports_section = "\n".join(ports) if ports else "          # No ports specified"
        
        manifest = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: agency-{config.environment}
  labels:
    app: agency
    environment: {config.environment}
spec:
  replicas: {config.replicas}
  selector:
    matchLabels:
      app: agency
      environment: {config.environment}
  template:
    metadata:
      labels:
        app: agency
        environment: {config.environment}
    spec:
      containers:
      - name: agency
        image: agency-{config.environment}:{config.version}
        ports:
{ports_section}
        env:
{env_section}
        resources:
          requests:
            memory: "{config.resources.get('memory', '512Mi') if config.resources else '512Mi'}"
            cpu: "{config.resources.get('cpu', '500m') if config.resources else '500m'}"
          limits:
            memory: "{config.resources.get('memory', '1Gi') if config.resources else '1Gi'}"
            cpu: "{config.resources.get('cpu', '1000m') if config.resources else '1000m'}"
        livenessProbe:
          httpGet:
            path: {config.health_check_path}
            port: {config.ports[0] if config.ports else 8000}
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: {config.readiness_check_path}
            port: {config.ports[0] if config.ports else 8000}
          initialDelaySeconds: 5
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: agency-service-{config.environment}
spec:
  selector:
    app: agency
    environment: {config.environment}
  ports:
    - protocol: TCP
      port: {config.ports[0] if config.ports else 8000}
      targetPort: {config.ports[0] if config.ports else 8000}
  type: LoadBalancer
"""
        return manifest
    
    async def _deploy_aws(self, config: DeploymentConfig) -> bool:
        """Deploy to AWS (placeholder implementation)"""
        self._logger.info("Deploying to AWS")
        # This would integrate with AWS services like ECS, Lambda, EC2, etc.
        # For now, just log the intended deployment
        self._logger.info(f"AWS deployment would deploy version {config.version} to {config.environment}")
        return True  # Placeholder - would implement actual AWS deployment
    
    async def _deploy_azure(self, config: DeploymentConfig) -> bool:
        """Deploy to Azure (placeholder implementation)"""
        self._logger.info("Deploying to Azure")
        # This would integrate with Azure services like AKS, Functions, VMs, etc.
        # For now, just log the intended deployment
        self._logger.info(f"Azure deployment would deploy version {config.version} to {config.environment}")
        return True  # Placeholder - would implement actual Azure deployment
    
    async def _deploy_gcp(self, config: DeploymentConfig) -> bool:
        """Deploy to GCP (placeholder implementation)"""
        self._logger.info("Deploying to GCP")
        # This would integrate with GCP services like GKE, Cloud Run, Compute Engine, etc.
        # For now, just log the intended deployment
        self._logger.info(f"GCP deployment would deploy version {config.version} to {config.environment}")
        return True  # Placeholder - would implement actual GCP deployment
    
    async def _deploy_custom(self, config: DeploymentConfig) -> bool:
        """Deploy using custom deployment logic"""
        self._logger.info("Deploying using custom deployment logic")
        # This would allow for custom deployment scripts or logic
        # Could execute custom deployment scripts, call APIs, etc.
        self._logger.info(f"Custom deployment for {config.environment}")
        return True  # Placeholder - would implement custom logic


class DeploymentOrchestrator:
    """Orchestrates complex multi-step deployments"""
    
    def __init__(self):
        self.deployment_manager = DeploymentManager()
        self._logger = get_logger(__name__)
    
    async def deploy_multi_stage(self, stages: List[Dict[str, Any]]) -> bool:
        """Deploy through multiple stages (dev -> staging -> prod)"""
        for stage in stages:
            config_name = stage["config"]
            pre_hook = stage.get("pre_hook")
            post_hook = stage.get("post_hook")
            
            if pre_hook:
                self._logger.info(f"Running pre-deployment hook for {config_name}")
                await self._execute_hook(pre_hook)
            
            success = await self.deployment_manager.deploy(config_name)
            if not success:
                self._logger.error(f"Deployment failed at stage: {config_name}")
                return False
            
            if post_hook:
                self._logger.info(f"Running post-deployment hook for {config_name}")
                await self._execute_hook(post_hook)
        
        return True
    
    async def _execute_hook(self, hook_config: Dict[str, Any]):
        """Execute a deployment hook (script, command, etc.)"""
        hook_type = hook_config.get("type", "command")
        hook_data = hook_config.get("data", "")
        
        if hook_type == "command":
            result = subprocess.run(hook_data, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception(f"Hook command failed: {result.stderr}")
        elif hook_type == "script":
            # Execute a Python script
            exec(hook_data)
        # Add more hook types as needed


# Global deployment manager instance
deployment_manager = DeploymentManager()
deployment_orchestrator = DeploymentOrchestrator()


def get_deployment_manager() -> DeploymentManager:
    """Get the global deployment manager"""
    return deployment_manager


def get_deployment_orchestrator() -> DeploymentOrchestrator:
    """Get the global deployment orchestrator"""
    return deployment_orchestrator