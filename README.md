[![Build Status](https://travis-ci.org/EqualExpertsMicroDC/ee-microdc-init.svg)](https://travis-ci.org/EqualExpertsMicroDC/ee-microdc-init)

# ee-microdc-init
A python package to manage a pick 'n' mix Kubernetes infrastructure on AWS

### Install
`pip install git+https://github.com/EqualExpertsMicroDC/ee-microdc-init`

#### or run with docker
`docker build -t microdc .`
`docker run microdc microdc --help`

### Usage
`microdc --help`

### Tests
`$ ./test.sh`


### Bring up a MicroDC environtment
This will bring up kubernetes clusters in AWS accounts.  In this example we will spin up a single cluster called dev.

1. First we create a config.yml
```
```

