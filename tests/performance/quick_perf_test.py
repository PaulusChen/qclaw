"""
TEST-PERF-001: 性能基准测试 (快速版)
"""
import requests
import time
import statistics

print("=" * 60)
print("TEST-PERF-001: 性能基准测试")
print("=" * 60)

# 测试前端加载
print("\n[1/3] 前端加载测试...")
frontend_url = "http://localhost:3000"
times = []

for i in range(10):
    start = time.time()
    response = requests.get(frontend_url, timeout=10)
    elapsed = (time.time() - start) * 1000
    times.append(elapsed)
    print(f"  [{i+1}] {elapsed:.2f}ms - {len(response.content)} bytes")

avg = statistics.mean(times)
p95 = sorted(times)[int(len(times) * 0.95)]
print(f"\n前端加载性能:")
print(f"  平均：{avg:.2f}ms")
print(f"  P95: {p95:.2f}ms")
print(f"  状态：{'✅ 优秀' if avg < 100 else '⚠️ 一般' if avg < 500 else '❌ 慢'}")

# 测试 API 响应
print("\n[2/3] API 响应测试...")
api_urls = [
    "http://localhost:8000/api/news",
    "http://localhost:8000/api/market",
]

for url in api_urls:
    times = []
    try:
        for i in range(10):
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
        
        avg = statistics.mean(times)
        print(f"  {url}: {avg:.2f}ms ({response.status_code})")
    except Exception as e:
        print(f"  {url}: ❌ {str(e)}")

# 测试 Redis
print("\n[3/3] Redis 性能测试...")
import subprocess

try:
    # 使用 redis-cli 测试
    result = subprocess.run(
        ["docker", "compose", "exec", "-T", "redis", "redis-cli", "--intrinsic-latency", "1"],
        capture_output=True, text=True, timeout=5
    )
    print(f"  Redis 延迟测试：{result.stdout[:200] if result.stdout else 'N/A'}")
except Exception as e:
    print(f"  Redis 测试：⚠️ {str(e)}")

print("\n" + "=" * 60)
print("✅ TEST-PERF-001: 性能基准测试完成")
print("=" * 60)
