from setuptools import setup, find_packages

setup(
    name='converterLib',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        # List any required dependencies here
        'flask<2.0.0',
        'Werkzeug<2.0.0',
        'flask-restx==1.0.3',
        'MarkupSafe',
        'redis',
        'rq',
        'flask-swagger-ui==4.11.1',
        'entrypoints==0.3.0',
        'mccabe==0.6.0',
        'flake8'
    ],
)
