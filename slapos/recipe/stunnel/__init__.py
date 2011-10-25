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

class Recipe(GenericBaseRecipe):

  def _options(self, options):
    self.isClient = self.optionIsTrue('client', default=False)
    if self.isClient:
      self.logger.info("Client mode")
    else:
      self.logger.info("Server mode")

  def install(self):
    path_list = []
    conf = {}

    for type_ in ['remote', 'local']:
      for data in ['host', 'port']:
        confkey, opt = ['%s%s%s' % (type_, i, data) for i in ['_', '-']]
        conf[confkey] = self.options[opt]

    pid_file = self.options['pid-file']
    conf.update(pid_file=pid_file)
    path_list.append(pid_file)

    log_file = self.options['log-file']
    conf.update(log=log_file)

    if self.isClient:
      template = self.getTemplateFilename('client.conf.in')

    else:
      template = self.getTemplateFilename('server.conf.in')
      key = self.options['key-file']
      cert = self.options['cert-file']
      conf.update(key=key, cert=cert)

    conf_file = self.createFile(
      self.options['config-file'],
      self.substituteTemplate(template, conf))
    path_list.append(conf_file)

    wrapper = self.createPythonScript(
      self.options['wrapper'],
      'slapos.recipe.librecipe.execute.execute',
      [self.options['stunnel-binary'], conf_file]
    )
    path_list.append(wrapper)

    return path_list
