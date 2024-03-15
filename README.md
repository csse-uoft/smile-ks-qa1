# smile_ks_qa1
SMILE Knowledge Source: QA1




# Setup

#### 1 GraphDB Installation
- [GraphDB](https://www.ontotext.com/products/graphdb/) can be installed for your distribution.
- Make sure it's running port `7200`, e.g. [http://localhost:7200](http://localhost:7200).
- Make sure you have GraphDB running on [http://localhost:7200](http://localhost:7200).

#### 2 GraphDB Repository Creation
- For testing, make sure the username and password are set to `admin`
- Create a new test repository. Go to [http://localhost:7200](http://localhost:7200)
  - Create new repository:
    - Name the repository (Repository ID) as `smile`
    - Set context index to True *(checked).
    - Set query timeout to 45 second.
    - Set the `Throw exception on query timeout` checkmark to True (checked)
    - Click on create repository.
  - Make sure the repository rin in "Running" state.
- [See instruction below for troubleshooting](#user-content-graphdb-and-docker-configuration)


#### 3 GraphDB Configuration
A few notes on configurting SMILE to connect to the database.
- The main SMILE Flask application can be configured in the [config/local_config.yml](config/local_config.yml) file.
- Knowledge source that are running in a Docker instance must use the "Docker" version of the config file: [config/local_config_test.yml](config/local_config_test.yml).



#### 4 Setup smile-ks-qa1
`conda env create -f PyQAWrapperQA1.yml`



## To run example
`conda activate PyQAWrapperQA1`
`cd src`
`python -m smile_ks_qa1.main`

