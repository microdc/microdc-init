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


### Bring up a MicroDC environment
This will bring up kubernetes clusters in AWS accounts.  In this example we will spin up a single cluster called dev.

0. Meet the prerequisites
```
TODO
```

1. First we create a config.yml
```
cat > config.yml << EOF
TODO
EOF
```
2. We run the global setup
```
microdc --config config.yml --account prod --stack global --tool terraform up --bootstrap
microdc --config config.yml --account prod --stack global --tool terraform up --bootstrap | sh
```

3. Initial cluster setup
```
microdc --config config.yml --account prod --tool kops up --env prod
microdc --config config.yml --account prod --tool kops up --env prod | sh
```

4. Complete setup around the edges.
```
microdc --config config.yml --account prod --stack service --tool terraform up --env prod
microdc --config config.yml --account prod --stack service --tool terraform up --env prod | sh
```

5. Validate our setup.
`kops validate cluster`

6. Deploy stack.
```
microdc --config config.yml --account prod --tool kubectl up --env prod
microdc --config config.yml --account prod --tool kubectl up --env prod | sh
```

### Extras - create developer and deployment users for the apps namespace
https://github.com/EqualExpertsMicroDC/apps-namespace
