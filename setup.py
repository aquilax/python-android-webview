from setuptools import setup

setup(
    name='python-android-webview',
    version='0.0.1',
    description='Python script to generate and build Android webview based apps',
    author='Evgeniy Vasilev',
    author_email='aquilax@gmail.com',
    url='https://github.com/aquilax/python-android-webview',
    packages=['paw'],
    package_data={'paw': [
        'templates/*'
    ]},
    entry_points={
        'console_scripts': [
            'paw = paw.cli:cli',
        ]
    }
)
