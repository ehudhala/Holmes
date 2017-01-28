#!/usr/bin/python
"""
This code is the code the service module suggests using.
It's bad but works.
"""
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
        print 'Started holmesd'
    elif cmd == 'stop':
        service.stop()
        print 'Stopped holmesd'
    elif cmd == 'restart':
        service.stop()
        print 'Stopped holmesd'
        service.start()
        print 'Started holmesd'
    elif cmd == 'status':
        if service.is_running():
            print "Service is running."
        else:
            print "Service is not running."
    else:
        sys.exit('Unknown command "%s".' % cmd)

