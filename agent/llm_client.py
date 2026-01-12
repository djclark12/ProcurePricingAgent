"""
Azure OpenAI client wrapper.

Uses the official OpenAI Python SDK with Azure configuration.
"""

import os
from functools import lru_cache

from dotenv import load_dotenv
from openai import AzureOpenAI


def _load_env_vars() -> dict[str, str]:
    """Load and validate required environment variables."""
    load_dotenv()

    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "OPENAI_API_VERSION",
        "AZURE_OPENAI_DEPLOYMENT",
    ]

    config = {}
    missing = []

    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            config[var] = value

    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            "Please copy .env.example to .env and fill in your Azure OpenAI credentials.\n"
            "See README.md for details."
        )

    return config


@lru_cache(maxsize=1)
def get_llm_client() -> AzureOpenAI:
    """
    Create and return a cached Azure OpenAI client.

    Returns:
        AzureOpenAI: Configured client instance.
    """
    config = _load_env_vars()

    client = AzureOpenAI(
        azure_endpoint=config["AZURE_OPENAI_ENDPOINT"],
        api_key=config["AZURE_OPENAI_API_KEY"],
        api_version=config["OPENAI_API_VERSION"],
    )

    return client


def get_deployment_name() -> str:
    """Get the Azure OpenAI deployment name."""
    load_dotenv()
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not deployment:
        raise EnvironmentError(
            "AZURE_OPENAI_DEPLOYMENT is not set. "
            "This should be your deployment name from Azure (not the model name)."
        )
    return deployment
