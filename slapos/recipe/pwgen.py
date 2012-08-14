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
import subprocess
import os

from slapos.recipe.librecipe import GenericBaseRecipe

class Recipe(GenericBaseRecipe):

  def _options(self, options):
    if not os.path.exists(self.options['file']):
      password = subprocess.check_output([self.options['pwgen-binary'], '-1']).strip()
      with open(self.options['file'], 'w') as password_file:
        password_file.write(password)
    else:
      with open(self.options['file'], 'r') as password_file:
        password = password_file.read()
    options['password'] = password

  update = install = lambda self: []

class StablePasswordGeneratorRecipe(GenericBaseRecipe):
  """
  The purpose of this class is to generate a password which doesn't change
  from one execution to the next (hence "stable"), so the generated password
  doesn't change on each slapgrid-cp execution.

  See GenericBaseRecipe.generatePassword .
  """

  def _options(self, options):
    options['password'] = self.generatePassword()

  update = install = lambda self: []
