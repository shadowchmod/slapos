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
import shutil
import os

from slapos.recipe.librecipe import GenericBaseRecipe

class Recipe(GenericBaseRecipe):

  def install(self):
    path_list = []

    # Copy application
    shutil.rmtree(self.options['htdocs'])
    shutil.copytree(self.options['source'],
                    self.options['htdocs'])

    # Install php.ini
    php_ini = self.createFile(os.path.join(self.options['php-ini-dir'],
                                           'php.ini'),
      self.substituteTemplate(self.getTemplateFilename('php.ini.in'),
        dict(tmp_directory=self.options['tmp-dir']))
    )
    path_list.append(php_ini)

    # Install apache
    apache_config = dict(
      pid_file=self.options['pid-file'],
      lock_file=self.options['lock-file'],
      ip=self.options['ip'],
      port=self.options['port'],
      error_log=self.options['error-log'],
      access_log=self.options['access-log'],
      document_root=self.options['htdocs'],
      php_ini_dir=self.options['php-ini-dir'],
    )
    httpd_conf = self.createFile(self.options['httpd-conf'],
      self.substituteTemplate(self.getTemplateFilename('apache.in'),
                              apache_config)
    )
    path_list.append(httpd_conf)

    wrapper = self.createPythonScript(self.options['wrapper'],
        'slapos.recipe.librecipe.execute.execute',
        [self.options['httpd-binary'], '-f', self.options['httpd-conf'],
         '-DFOREGROUND']
    )
    path_list.append(wrapper)

    mysql_conf = dict(mysql_database=self.options['mysql-database'],
                      mysql_user=self.options['mysql-username'],
                      mysql_password=self.options['mysql-password'],
                      mysql_host='%s:%s' % (self.options['mysql-host'],
                                            self.options['mysql-port']),
                     )

    directory, file_ = os.path.split(self.options['configuration'])

    path = self.options['htdocs']
    if directory:
      path = os.path.join(path, directory)
      if not os.path.exists(path):
        os.makedirs(path)
      if not os.path.isdir(path):
        raise OSError("Cannot create %r." % path)

    destination = os.path.join(path, file_)
    config = self.createFile(destination,
      self.substituteTemplate(self.options['template'], mysql_conf))
    path_list.append(config)

    return path_list