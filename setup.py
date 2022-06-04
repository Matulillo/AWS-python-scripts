from setuptools import setup

setup(
    name='ec2_manager',
    version='0.1',
    author='Carlos',
    author_email='crodriguezhervas@gmail.com',
    description='tool to manage EC2 instances',
    packages=['src'],
    url="https://github.com/Matulillo/AWS-python-scripts",
    install_requires=[
        'click',
        'boto3'
    ],
    entry_points='''
        [console_scripts]
        ec2_manager=src.ec2_manager:cli
    ''',


)