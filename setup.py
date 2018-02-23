from setuptools import setup, find_packages

setup(
    name='microdc-init',
    version='0.1dev',
    description='A python package to manage a pick `n` mix Kubernetes infrastructure on AWS',
    url='https://github.com/microdc/microdc-init',
    author='Alan Platt - Equal Experts',
    author_email='aplatt@equalexperts.com',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['Jinja2==2.10', 'PyYAML==3.12'],
    include_package_data=True,
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
