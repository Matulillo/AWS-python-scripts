# AWS-python-scripts
Repo for python scripts to manages AWS resources

'aws configure --profile default'

## Running 
pipenv shell
python src/ec2_manager.py

`pipenv run python src/ec2_manager.py <command> <--project PROJECT>`

*command* is list , start, stop
*subcommand* depends on command
*project* is project tag (optional)
