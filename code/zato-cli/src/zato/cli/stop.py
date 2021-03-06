# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, signal, sys

# Zato
from zato.cli import ManageCommand
from zato.common.util import get_haproxy_pidfile

class Stop(ManageCommand):
    """ Stops a Zato component
    """
    def signal(self, component_name, signal_name, signal_code, pidfile=None, component_dir=None):
        """ Sends a signal to a process known by its pidfile.
        """
        component_dir = component_dir or self.component_dir
        pidfile = pidfile or os.path.join(component_dir, 'pidfile')
        if not os.path.exists(pidfile):
            self.logger.error('No pidfile found in `%s`', pidfile)
            sys.exit(self.SYS_ERROR.FILE_MISSING)

        pid = open(pidfile).read().strip()
        if not pid:
            self.logger.error('Empty pidfile `%s`, did not attempt to stop `%s`', pidfile, component_dir)
            sys.exit(self.SYS_ERROR.NO_PID_FOUND)

        pid = int(pid)
        self.logger.debug('Will now send `%s` to pid `%s` (as found in `%s`)', signal_name, pid, pidfile)

        os.kill(pid, signal_code)
        os.remove(pidfile)

        self.logger.info('%s `%s` shutting down', component_name, component_dir)

    def _on_server(self, *ignored):
        self.signal('Server', 'SIGTERM', signal.SIGTERM)

    def stop_haproxy(self, component_dir):
        self.signal('Load-balancer', 'SIGTERM', signal.SIGTERM, get_haproxy_pidfile(component_dir), component_dir)

    def _on_lb(self, *ignored):
        self.stop_haproxy(self.component_dir)
        self.signal('Load-balancer\'s agent', 'SIGTERM', signal.SIGTERM)

    def _on_web_admin(self, *ignored):
        self.signal('Web admin', 'SIGTERM', signal.SIGTERM)
