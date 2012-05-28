# -*- coding: utf-8 -*-

"""
Copyright (C) 2012 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os, shutil
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import DEPLOYMENT_STATUS
from zato.common.odb.model import DeploymentPackage, DeploymentStatus
from zato.common.util import fs_safe_now
from zato.server.service.internal import AdminService

class Create(AdminService):
    """ Creates all the needed filesystem directories and files out of a deployment
    package stored in the ODB and starts all the services contained within the
    package.
    """
    class SimpleIO:
        input_required = ('package_id',)
        
    def backup_current_work_dir(self):
        
        # Save a few keystrokes
        last_backup_work_dir = self.server.hot_deploy_config.last_backup_work_dir
        current_work_dir = self.server.hot_deploy_config.current_work_dir
        backup_work_dir = self.server.hot_deploy_config.backup_work_dir
        backup_history= self.server.hot_deploy_config.backup_history
        backup_format = self.server.hot_deploy_config.backup_format
        
        # Safe as a directory name
        fs_now = fs_safe_now()
        
        # We want to grab the directory's contents right now, before we place the
        # new backup in there
        last_backup_contents = []
        for item in os.listdir(last_backup_work_dir):
            last_backup_contents.append(os.path.join(last_backup_work_dir, item))
            
        # First make the backup to the special 'last' directory
        last_backup_path = os.path.join(last_backup_work_dir, fs_now)
        shutil.make_archive(last_backup_path, backup_format, current_work_dir, verbose=True, logger=self.logger)
            
        # Now delete everything previously found in the last backup directory
        for item in last_backup_contents:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
            else:
                msg = "Could not delete [{}], it's neither file nor a directory, stat:[{}]".format(item, os.stat(item))
                self.logger.warn(msg)
        
        #print(self.server.base_dir, self.server.hot_deploy_config.current_work_dir, self.server.hot_deploy_config.backup_work_dir, self.server.hot_deploy_config.last_backup_work_dir)
        #print(3333, )
    
    def deploy_package(self, package_id):
        with closing(self.odb.session()) as session:
            dp = session.query(DeploymentPackage).\
                filter(DeploymentPackage.id==package_id).\
                one()
            
            print(22, dp.payload_name, dp.payload)

    def handle(self):
        self.backup_current_work_dir()
        self.deploy_package(self.request.input.package_id)
