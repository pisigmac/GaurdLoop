from setuptools import setup, find_packages

setup(
    name="guardloop-mcp",
    version="1.0.0",
    description="GuardLoop MCP Server — Agent Trust Layer as MCP tools",
    author="GuardLoop",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "guardloop-mcp=guardloop_mcp.server:main",
        ],
    },
    python_requires=">=3.10",
)
