from setuptools import setup, find_packages

setup(
    name='rename_smartly',
    version='1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'rename-smartly = rename_smartly.main:main'
        ]
    },
)
