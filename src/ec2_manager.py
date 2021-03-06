from email.policy import default
import boto3
import botocore
import click

session = boto3.Session(profile_name='default')
ec2 = session.resource('ec2')


def filter_instances(project, name):
    instances =[]

    if project and name:
        filter = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filter)
        filter = [{'Name':'tag:Name', 'Values':[name]}]
        instances = ec2.instances.filter(Filters=filter)
    elif project:
        filter = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filter)
    elif name:
        filter = [{'Name':'tag:Name', 'Values':[name]}]
        instances = ec2.instances.filter(Filters=filter)
    else:
        instances = ec2.instances.all()
    return instances


def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'


@click.group()
def cli():
    """scripts manages snapshots"""

#-------------------------------------------------------------------------------------------------
@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None, help="Only volumes for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
def list_volumes(project, name):
    "List EC2 volumes"
    instances = filter_instances(project,name)

    for i in instances:
        for v in i.volumes.all():
            print(", ".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + "GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return
#-------------------------------------------------------------------------------------------------

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None, help="Only snapshots for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True, help= "List all snapshots for each volume not only the most recent")
def list_snapshots(project, name, list_all):
    "List EC2 snapshots"
    instances = filter_instances(project, name)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(", ".join((
                s.id,
                v.id,
                i.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
                if s.state == 'completed' and not list_all: break
    return
#-------------------------------------------------------------------------------------------------

@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
def list_instances(project, name):
    "List EC2 instances"
    instances = filter_instances(project, name)
    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            tags.get('Project', '<no project>'),
            tags.get('Name'),
            str(i.public_ip_address),
            str(i.private_ip_address)
            )))

    return

@instances.command('stop')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
def stop_instances(project, name):
    "Stop EC2 instances"
    instances = filter_instances(project, name)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}. ".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
def start_instances(project, name):
    "Start EC2 instances"
    instances = filter_instances(project, name)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}. ".format(i.id) + str(e))
            continue

    return


@instances.command('snapshot')
@click.option('--project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--name', default=None, help="Only volumes for name (tag Name:<name>)")
def creates_snapshots(project, name):
    "Creates snapshots for EC2 instances"
    instances = filter_instances(project, name)
    for i in instances:
        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print("Skipping snapshot of {0}".format(v.id))
                continue
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by ec2_manager script")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()
    print('Job done!!')
    return

if __name__ == '__main__':
    cli()
