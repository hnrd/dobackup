import argparse
import subprocess
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from docker import Client


scheduler = BackgroundScheduler()


def backup(socket, outdir, stack, services):
    api = Client(base_url=args.socket)
    for service in services:
        containers = api.containers(
            filters={
                'label': "io.rancher.project_service.name={}/{}".format(
                    stack,
                    service,
                )
            }
        )
    
        for container in containers:
    
            for mount in container.get('Mounts'):
                name = mount.get('Name')
                source = mount.get('Source')
      
                outfile="{outdir}/{stack}-{service}-{name}-{date}-{container}.tgz".format(
                    outdir=outdir,
                    stack=stack,
                    service=service,
                    name=name,
                    date=datetime.now().strftime('%Y%m%d-%H%M%S'),
                    container=container.get('Id')[:8],
                )
                subprocess.call([
                    "tar",
                    "-cpzf",
                    outfile,
                    source,
                ])

parser = argparse.ArgumentParser(description="backup a rancher services docker volumes")
parser.add_argument('socket', default='unix://var/run/docker.sock',
                    help="docker socket")
parser.add_argument('outdir')
parser.add_argument('stack', help="rancher stack name")
parser.add_argument('services', metavar='service', nargs='+',
                    help="rancher service names")
args = parser.parse_args()
backup(args.socket, args.outdir, args.stack, args.services)

scheduler.start()
scheduler.add_job(
    func=backup,
    trigger='interval',
    days=1,
    args=(args.socket, args.outdir, args.stack, args.services),
)
try:
    while True:
        time.sleep(20)
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()
