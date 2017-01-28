#!/usr/bin/python
from service import Service

from holmes.scheduling import schedule_forever

class HolmesService(Service):
    def run(self):
        schedule_forever()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    service = HolmesService('holmesd', pid_dir='/tmp')

    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
    elif cmd == 'restart':
        service.stop()
        service.start()
    elif cmd == 'status':
        if service.is_running():
            print "Service is running."
        else:
            print "Service is not running."
    else:
        sys.exit('Unknown command "%s".' % cmd)

