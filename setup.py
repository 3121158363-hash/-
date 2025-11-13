# setup.py
from setuptools import setup, find_packages

setup(
    name="intellect-agent",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'pytest',
        'gunicorn',
        'celery',
        'redis',
        'pandas',
    ],
)
