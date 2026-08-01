from setuptools import setup, find_packages

setup(
    name="guardloop-bridge",
    version="1.0.0",
    description="GuardLoop Webhook Bridge — Relay agent webhooks to GuardLoop",
    author="GuardLoop",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.111.0",
        "uvicorn[standard]>=0.30.0",
        "httpx>=0.27.0",
    ],
    entry_points={
        "console_scripts": [
            "guardloop-bridge=guardloop_bridge.main:app",
        ],
    },
    python_requires=">=3.10",
)
