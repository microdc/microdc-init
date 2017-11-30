from setuptools import setup, find_packages

setup(
    name='ee-microdc-init',
    version='0.1dev',
    description='A python package to manage a pick `n` mix Kubernetes infrastructure on AWS',
    url='https://github.com/EqualExpertsMicroDC/ee-microdc-init',
    author='Alan Platt - Equal Experts',
    author_email='aplatt@equalexperts.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    keywords='cli kubernetes terraform aws',
    license='Apache',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'microdc=microdc:main',
        ],
    },
)
