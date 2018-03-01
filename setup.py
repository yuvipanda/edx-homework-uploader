from setuptools import setup, find_packages

setup(
    name='homeworkuploader',
    version='0.1',
    description='Upload homeworks from EdX',
    author='Yuvi Panda',
    author_email='yuvipanda@gmail.com',
    license='3 Clause BSD',
    packages=find_packages(),
    install_requires=[
        'tornado',
        'oauthlib==2.*'
    ]
)
