##############################################################################
#
# Copyright (c) 2011 Vifib SARL and Contributors. All Rights Reserved.
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
import shutil
from slapos.recipe.librecipe import GenericSlapRecipe
from subprocess import Popen
import sys

class Recipe(GenericSlapRecipe):
  def install(self):
    path_list = []
    poc_location = self.buildout['pocdirectory']['poc']

    # Generate os-config.xml
    os_configuration_parameter_dict = dict(
        userid=self.options['userid'],
        password=self.options['password'],
        domain=self.options['domain'],
    )
    os_config_file = self.createFile(self.options['os-config'],
        self.substituteTemplate(self.getTemplateFilename('os_config.xml.in'),
        os_configuration_parameter_dict))
    path_list.append(os_config_file)
    
    # Put modified accords configuration file
    accords_configuration_parameter_dict = dict(
        listen_ip = self.options['listen-ip']
    )
    accords_configuration_file_location = self.createFile(
        self.options['accords-configuration-file'],
        self.substituteTemplate(self.getTemplateFilename('accords.ini.in'),
        accords_configuration_parameter_dict))
    path_list.append(accords_configuration_file_location)

    # Initiate configuration
    Popen('./accords-config',
          cwd=poc_location
    ).communicate()

    # Generate manifest
    manifest_origin_location = self.options['manifest-source']
    manifest_location = self.options['manifest-destination']
    
    shutil.copy(manifest_origin_location, manifest_location)
    path_list.append(manifest_location)

    # Generate wrapper
    wrapper_config_dict = dict(
        python_location=sys.executable,
        poc_location=poc_location,
        manifest_name=self.options['manifest-name'],
        # XXX this is workaround
        accords_lib_directory=self.options['accords_lib_directory'])

    wrapper_location = self.createPythonScript(self.options['accords-wrapper'],
        '%s.accords.runAccords' % __name__,
        wrapper_config_dict)
    path_list.append(wrapper_location)

    return path_list
