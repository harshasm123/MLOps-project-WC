"""Configuration management for the MLOps platform."""

from .aws_config import AWSConfig, get_config

__all__ = ['AWSConfig', 'get_config']
