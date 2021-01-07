from setuptools import setup, find_packages

setup(
    name='proxy',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Makes and handles http requests using proxy servers.',
    long_description=open('README.md').read(),
    install_requires=[
        'certifi==2018.11.29',
        'chardet==3.0.4',
        'idna==2.8',
        'lxml==4.6.2',
        'requests==2.21.0',
        'urllib3==1.24.1'
    ],
    url='https://github.com/NOVOMOTUS/proxy',
    author='Novomotus',
    author_email='info@novomotus.com'
)