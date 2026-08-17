from setuptools import find_packages, setup

setup(
    name="audit-ai",
    version="0.1.0",
    description="Python SDK for the audit-ai LLM audit trail",
    packages=find_packages(),
    install_requires=["httpx>=0.27"],
    python_requires=">=3.9",
)
