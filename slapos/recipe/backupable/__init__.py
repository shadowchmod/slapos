##############################################################################
#
# Copyright (c) 2010 Vifib SARL and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
from slapos.recipe.librecipe import GenericBaseRecipe

import sys
import os


class Backupable(GenericBaseRecipe):
  """ Inheriting from this class provides the installation of a backup
      script on the partition.
  """

  def __init__(self, buildout, name, options):
    """Recipe initialisation"""
    super(Backupable, self).__init__(buildout, name, options)
    param_dict = self.getComputerPartitionInstanceParameterDict()

    if 'bully' in param_dict:
      self.createBackupScript(param_dict)

  def createBackupScript(self, param_dict):
    self_id = int(param_dict['number'])
    ip = param_dict['ip-list'].split()

    slap_connection = self.buildout['slap-connection']

    path_conf = os.path.join(self.options['script'], 'conf.in')
    path_bully = os.path.join(self.options['script'], param_dict['script'])

    bully_conf = dict(self_id=self_id,
                      ip_list=ip,
                      executable=sys.executable,
                      syspath=sys.path,
                      server_url=slap_connection['server-url'],
                      key_file=slap_connection.get('key-file'),
                      cert_file=slap_connection.get('cert-file'),
                      computer_id=slap_connection['computer-id'],
                      partition_id=slap_connection['partition-id'],
                      software=slap_connection['software-release-url'],
                      namebase=param_dict['namebase'],
                      confpath=path_conf)
    try:
      conf = self.createFile(path_conf,
                             self.substituteTemplate(
                             self.getTemplateFilename('conf.in.in'),
                             bully_conf))

      script = self.createExecutable(path_bully,
                                     self.substituteTemplate(
                                     self.getTemplateFilename('bully.py.in'),
                                     bully_conf))

      wrapper = self.createPythonScript(
          os.path.join(self.options['run'], param_dict['wrapper']),
          'slapos.recipe.librecipe.execute.execute',
          [path_bully])
    except IOError:
      pass
