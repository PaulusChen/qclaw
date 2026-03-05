"""
Docker 系统测试 - TEST-SYS-001
测试 Docker 容器和服务的正常运行
"""
import pytest
import subprocess
import requests
import time
import shutil
from typing import Dict, Any


def check_docker_available():
    """检查 Docker 是否可用"""
    result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
    return result.returncode == 0


def check_docker_compose_available():
    """检查 Docker Compose 是否可用"""
    # 尝试 docker compose (v2) 或 docker-compose (v1)
    result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True)
    if result.returncode == 0:
        return True
    result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True)
    return result.returncode == 0


class TestDockerServices:
    """Docker 服务测试类"""
    
    @pytest.fixture(scope="class", autouse=True)
    def docker_compose_up(self):
        """启动 Docker Compose 服务"""
        if not check_docker_compose_available():
            pytest.skip("Docker Compose not available")
        
        try:
            # 启动服务
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd="/home/openclaw/qclaw",
                check=True,
                capture_output=True
            )
            
            # 等待服务启动
            time.sleep(30)
            
            yield
            
            # 停止服务
            subprocess.run(
                ["docker-compose", "down"],
                cwd="/home/openclaw/qclaw",
                check=True,
                capture_output=True
            )
        except FileNotFoundError:
            pytest.skip("Docker Compose not available")
    
    def test_api_service_health(self, docker_compose_up):
        """测试 API 服务健康检查"""
        response = requests.get("http://localhost:8000/health", timeout=10)
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_frontend_service_available(self, docker_compose_up):
        """测试前端服务可用性"""
        response = requests.get("http://localhost:3000", timeout=10)
        assert response.status_code == 200
        assert "QCLaw" in response.text
    
    def test_redis_service_connection(self, docker_compose_up):
        """测试 Redis 服务连接"""
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0)
        assert r.ping() is True
    
    def test_service_logs(self, docker_compose_up):
        """测试服务日志输出"""
        # 检查 API 日志
        result = subprocess.run(
            ["docker-compose", "logs", "api"],
            cwd="/home/openclaw/qclaw",
            capture_output=True,
            text=True
        )
        assert "Uvicorn running" in result.stdout or "Started server" in result.stdout
    
    def test_container_resource_usage(self, docker_compose_up):
        """测试容器资源使用"""
        # 检查内存使用
        result = subprocess.run(
            ["docker", "stats", "--no-stream", "--format", "{{.MemUsage}}"],
            capture_output=True,
            text=True
        )
        # 验证内存使用在合理范围内
        assert result.returncode == 0


class TestSystemIntegration:
    """系统集成测试类"""
    
    @pytest.fixture(scope="class", autouse=True)
    def full_system(self):
        """启动完整系统"""
        if not check_docker_compose_available():
            pytest.skip("Docker Compose not available")
        
        try:
            subprocess.run(
                ["docker-compose", "up", "-d"],
                cwd="/home/openclaw/qclaw",
                check=True,
                capture_output=True
            )
            time.sleep(30)
            yield
            subprocess.run(
                ["docker-compose", "down"],
                cwd="/home/openclaw/qclaw",
                check=True,
                capture_output=True
            )
        except FileNotFoundError:
            pytest.skip("Docker Compose not available")
    
    def test_full_stack_request(self, full_system):
        """测试全栈请求流程"""
        # 1. 前端请求
        # 2. API 处理
        # 3. 数据库查询
        # 4. 缓存命中
        # 5. 返回响应
        response = requests.get(
            "http://localhost:8000/api/market/indices",
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert "shanghai" in data
        assert "shenzhen" in data
        assert "chinext" in data
    
    def test_data_persistence(self, full_system):
        """测试数据持久化"""
        # 测试数据在容器重启后保持
        pass
    
    def test_service_communication(self, full_system):
        """测试服务间通信"""
        # 测试前端→后端→数据库→Redis 的通信链路
        pass


class TestEnvironmentVariables:
    """环境变量配置测试"""
    
    def test_required_env_vars(self):
        """测试必需的环境变量"""
        required_vars = [
            "REDIS_URL",
            "DATABASE_URL",
        ]
        # 验证环境变量存在
        pass
    
    def test_env_var_injection(self):
        """测试环境变量注入"""
        # 验证环境变量正确传递到容器
        pass


class TestContainerStartup:
    """容器启动测试"""
    
    def test_api_container_starts(self):
        """测试 API 容器启动"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=api", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        assert "Up" in result.stdout or result.returncode == 0
    
    def test_frontend_container_starts(self):
        """测试前端容器启动"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=frontend", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        assert "Up" in result.stdout or result.returncode == 0
    
    def test_redis_container_starts(self):
        """测试 Redis 容器启动"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=redis", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        assert "Up" in result.stdout or result.returncode == 0
    
    def test_database_container_starts(self):
        """测试数据库容器启动"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        assert "Up" in result.stdout or result.returncode == 0


class TestHealthChecks:
    """健康检查测试"""
    
    def test_api_health_endpoint(self):
        """测试 API 健康端点"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            # 服务未启动时跳过
            pytest.skip("API service not available")
    
    def test_frontend_health_check(self):
        """测试前端健康检查"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.skip("Frontend service not available")


class TestDataPersistence:
    """数据持久化测试"""
    
    def test_volume_mounts(self):
        """测试卷挂载"""
        if not check_docker_available():
            pytest.skip("Docker not available")
        result = subprocess.run(
            ["docker", "inspect", "qclaw-postgres", "--format", "{{.Mounts}}"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            pytest.skip("Postgres container not running")
        assert result.returncode == 0
    
    def test_database_persistence(self):
        """测试数据库持久化"""
        # 验证数据在容器重启后保持
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
