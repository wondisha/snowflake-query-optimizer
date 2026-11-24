"""Workaround for Windows AppStore Python 3.13 compatibility with snowflake-connector."""

import os
import sys
import platform as _platform

# CRITICAL: Remove conflicting environment variables BEFORE importing anything that uses them
# These override the Anthropic API and redirect to localhost
env_vars_to_remove = [
    'ANTHROPIC_BASE_URL',
    'ANTHROPIC_AUTH_TOKEN',
    'OPENAI_API_BASE',
    'OPENAI_API_KEY'
]

for var in env_vars_to_remove:
    if var in os.environ:
        del os.environ[var]

_original_libc_ver = _platform.libc_ver

def patched_libc_ver():
    """Patched version that handles Windows AppStore Python."""
    try:
        return _original_libc_ver()
    except (OSError, ValueError):
        return ('libc', '')

# Apply the patch
_platform.libc_ver = patched_libc_ver


