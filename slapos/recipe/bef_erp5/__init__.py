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
import slapos.recipe.erp5
import os
import pkg_resources
import zc.buildout
import sys
import netaddr

BEF_TIMEZONE = 'BST'

def validLoopBackAddress(ip):
  if netaddr.IPAddress(ip).is_loopback():
    return True
  else:
    return False

def validPublicAddress(ip):
  return not validLoopBackAddress(ip)

class Recipe(slapos.recipe.erp5.Recipe):
  site_id = 'erp5'

  def getLocalIPv4Address(self):
    """Returns local IPv4 address available on partition"""
    # XXX: Lack checking for locality of address
    if self.development:
      # XXX: Development superhack.
      return slapos.recipe.erp5.Recipe.getLocalIPv4Address(self)
    return self._getIpAddress(validLoopBackAddress)

  def getGlobalIPv6Address(self):
    """Returns global IPv6 address available on partition"""
    if self.development:
      # XXX: Development superhack.
      return slapos.recipe.erp5.Recipe.getGlobalIPv6Address(self)
    # XXX: Lack checking for globality of address

    return self._getIpAddress(validPublicAddress)

  def _getZeoClusterDict(self):
    site_path = '/erp5/'
    return {
        '/': (self._requestZeoFileStorage('Zeo Server 1', 'main'),
          site_path + 'account_module'),
        site_path + 'portal_activities': (self._requestZeoFileStorage('Zeo Server 1',
          'portal_activities'), None),
        site_path + 'task_report_module': (self._requestZeoFileStorage('Zeo Server 1',
          'task_report_module'), None),
        site_path + 'video_request_module': (self._requestZeoFileStorage('Zeo Server 1',
          'video_request_module'), None),
        site_path + 'bug_module': (self._requestZeoFileStorage('Zeo Server 1',
          'bug_module'), None),
        site_path + 'portal_simulation': (self._requestZeoFileStorage('Zeo Server 1',
          'portal_simulation'), None),
        site_path + 'notice_transfer_request_module': (self._requestZeoFileStorage(
          'Zeo Server 1', 'notice_transfer_request_module'), None),
        site_path + 'accounting_module': (self._requestZeoFileStorage('Zeo Server 1',
          'accounting_module'), None),
        site_path + 'task_module': (self._requestZeoFileStorage('Zeo Server 1',
          'task_module'), None),

        site_path + 'video_module': (self._requestZeoFileStorage('Zeo Server 2',
          'video_module'), None),

        site_path + 'event_module': (self._requestZeoFileStorage('Zeo Server 3',
          'event_module'), None),
        site_path + 'support_request_module': (self._requestZeoFileStorage(
          'Zeo Server 3', 'support_request_module'), None),

        site_path + 'person_module': (self._requestZeoFileStorage('Zeo Server 4',
          'person_module'), None),
        site_path + 'organisation_module': (self._requestZeoFileStorage('Zeo Server 4',
          'organisation_module'), None),
        # SyncML functionnality is not used anymore in this project.
        # No need to keep compatibility with previous data
#         site_path + 'portal_synchronizations': (self._requestZeoFileStorage(
#           'Zeo Server 4', 'portal_synchronizations'), None),

        site_path + 'scanned_document_module': (self._requestZeoFileStorage(
          'Zeo Server 5', 'scanned_document_module'), None),
        site_path + 'item_module': (self._requestZeoFileStorage('Zeo Server 5',
          'item_module'), None),
        site_path + 'document_module': (self._requestZeoFileStorage('Zeo Server 5',
          'document_module'), None),
        site_path + 'image_module': (self._requestZeoFileStorage('Zeo Server 5',
          'image_module'), None),
        site_path + 'external_source_module': (self._requestZeoFileStorage(
          'Zeo Server 5', 'external_source_module'), None),
    }

  def installProductionMysql(self):
    mysql_conf = self.installMysqlServer(self.getGlobalIPv6Address(), 45678,
        template_filename=pkg_resources.resource_filename(__name__,
          'template/my.cnf.in'), parallel_test_database_amount=1,
          mysql_conf=dict(innodb_buffer_pool_size='10G'), with_backup=False)
    self.installMysqldumpBackup()
    self.setConnectionDict(dict(
      mysql_url='%(mysql_database)s@%(ip)s:%(tcp_port)s %(mysql_user)s %(mysql_password)s' % mysql_conf,
    ))
    return self.path_list

  def installProductionApplication(self):
    site_check_path = '/%s/getId' % self.site_id
    access_control_string = self.parameter_dict['backend_acl_string']
    ca_conf = self.installCertificateAuthority()
    backend_key, backend_certificate = self.requestCertificate('Login Based Access')
    memcached_conf = self.installMemcached(ip=self.getLocalIPv4Address(),
        port=11000)
    conversion_server_conf = self.installConversionServer(
        self.getLocalIPv4Address(), 23000, 23060)
    user, password = self.installERP5()
    ip = self.getLocalIPv4Address()
    mount_point_zeo_dict = self._getZeoClusterDict()
    zeo_conf = self.installZeo(ip)
    zodb_configuration_list = []
    known_tid_storage_identifier_dict = {}
    for mount_point, (storage_dict, check_path) in mount_point_zeo_dict.iteritems():
      known_tid_storage_identifier_dict[
        (((storage_dict['ip'],storage_dict['port']),), storage_dict['storage_name'])
        ] = (zeo_conf[storage_dict['storage_name']]['path'], check_path or mount_point)
      zodb_configuration_list.append(self.substituteTemplate(
        self.getTemplateFilename('zope-zeo-snippet.conf.in'), dict(
        storage_name=storage_dict['storage_name'],
        address='%s:%s' % (storage_dict['ip'], storage_dict['port']),
        mount_point=mount_point
        )))
    tidstorage_config = dict(host=self.getLocalIPv4Address(), port='6001')
    zodb_configuration_string = '\n'.join(zodb_configuration_list)
    zope_port = 12000
    # One Distribution Node
    zope_port +=1
    self.installZope(ip, zope_port, 'zope_distribution',
        with_timerservice=True,
        zodb_configuration_string=zodb_configuration_string,
        tidstorage_config=tidstorage_config,
        zope_environment=dict(TZ=BEF_TIMEZONE))
    # Two Activity Nodes
    for i in (1, 2):
      zope_port += 1
      self.installZope(ip, zope_port, 'zope_activity_%s' % i,
        with_timerservice=True,
        zodb_configuration_string=zodb_configuration_string,
        tidstorage_config=tidstorage_config,
        zope_environment=dict(TZ=BEF_TIMEZONE))
    # Eight Working Nodes (Human access)
    login_url_list = []
    for i in (1, 2, 3, 4, 5, 6, 7, 8):
      zope_port += 1
      login_url_list.append(self.installZope(ip, zope_port,
        'zope_login_%s' % i, with_timerservice=False,
        zodb_configuration_string=zodb_configuration_string,
        tidstorage_config=tidstorage_config,
        zope_environment=dict(TZ=BEF_TIMEZONE)))
    login_haproxy = self.installHaproxy(ip, 15001, 'login', site_check_path,
        login_url_list)
    # One Web Node
    zope_port += 1
    web_url_list = [self.installZope(ip, zope_port, 'zope_web',
        with_timerservice=True,
        zodb_configuration_string=zodb_configuration_string,
        tidstorage_config=tidstorage_config,
        thread_amount=10, zope_environment=dict(TZ=BEF_TIMEZONE))]
    web_haproxy = self.installHaproxy(ip, 15002, 'web', site_check_path,
        web_url_list)
    apache_web = self.installBackendApache(self.getGlobalIPv6Address(), 15001,
        web_haproxy, backend_key, backend_certificate, suffix='_web',
        access_control_string=access_control_string)

    # One Admin Node
    zope_port += 1
    admin_url_list = [self.installZope(ip, zope_port, 'zope_admin',
        with_timerservice=True,
        zodb_configuration_string=zodb_configuration_string,
        tidstorage_config=tidstorage_config,
        zope_environment=dict(TZ=BEF_TIMEZONE))]
    admin_haproxy = self.installHaproxy(ip, 15003, 'admin', site_check_path,
        admin_url_list)
    apache_admin = self.installBackendApache(self.getGlobalIPv6Address(), 15002,
        admin_haproxy, backend_key, backend_certificate, suffix='_admin',
        access_control_string=access_control_string)

    self.installTidStorage(tidstorage_config['host'], tidstorage_config['port'],
        known_tid_storage_identifier_dict, 'http://'+login_haproxy)
    apache_login = self.installBackendApache(self.getGlobalIPv6Address(), 15000,
        login_haproxy, backend_key, backend_certificate, suffix='_user',
        access_control_string=access_control_string)

    memcached_conf = self.installMemcached(ip=self.getLocalIPv4Address(),
        port=11000)
    kumo_conf = self.installKumo(self.getLocalIPv4Address())
    self.setConnectionDict(dict(
      site_web_url=apache_web,
      site_admin_url=apache_admin,
      site_user_url=apache_login,
      site_user=user,
      site_password=password,
      memcached_url=memcached_conf['memcached_url'],
      kumo_url=kumo_conf['kumo_address'],
      conversion_server_url='%(conversion_server_ip)s:%(conversion_server_port)s' %
        conversion_server_conf,
      # openssl binary might be removed, as soon as CP environment will be
      # fully controlled
      openssl_binary=self.options['openssl_binary'],
      # As soon as there would be Vifib ERP5 configuration and possibility to
      # call it over the network this can be removed
      certificate_authority_path=ca_conf['certificate_authority_path'],
    ))
    return self.path_list

  def installProductionFrontend(self):
    frontend_key, frontend_certificate = self.requestCertificate(
        self.parameter_dict['frontend_name'])
    login_frontend = self.installFrontendZopeApache(
        self.getGlobalIPv6Address(), 18000,
        self.parameter_dict['frontend_name'],
        self.parameter_dict['frontend_path'],
        self.parameter_dict['backend_url'],
        self.parameter_dict['backend_path'], frontend_key,
        frontend_certificate,
        access_control_string=self.parameter_dict['frontend_acl_string'])

    self.setConnectionDict(dict(
      site_url='https://%s:%s%s' % (self.getGlobalIPv6Address(), 18000,
        self.parameter_dict['frontend_path']),
    ))
    return self.path_list

  def installMysqldumpBackup(self):
    backup_directory = self.createBackupDirectory('mysqldump')
    environment = dict(PATH='%s' % self.bin_directory)
    executable = os.path.join(self.bin_directory, 'mysqldump')
    mysql_socket = os.path.join(self.var_directory, 'run', 'mysqld.sock')
    mysqldump_opt = ['-u', 'root', '-S', mysql_socket, '--single-transaction',
      '--no-autocommit', '--opt']
    mysqldump_cron = os.path.join(self.cron_d, 'mysqldump')
    database = 'sanef_dms'
    cronfile = open(mysqldump_cron, 'w')
    cronfile.write("0 0 * * * %(mysqldump)s %(mysqldump_opt)s %(database)s | %(gzip)s > %(destination)s\n" % dict(
      mysqldump=executable, mysqldump_opt=' '.join(mysqldump_opt),
      database=database, gzip=self.options['gzip_binary'],
      destination=os.path.join(backup_directory, '%s.sql.gz' % database)
    ))
    for table in ['message', 'message_queue', 'portal_ids']:
      destination = os.path.join(backup_directory, '%s.%s.sql.gz' % (database,
        table))
      cronfile.write("0 0 * * * %(mysqldump)s %(mysqldump_opt)s %(database)s %(table)s | %(gzip)s > %(destination)s\n" % dict(
        mysqldump=executable, mysqldump_opt=' '.join(mysqldump_opt),
        database=database, gzip=self.options['gzip_binary'],
        table=table, destination=destination)
      )
    cronfile.close()
    self.path_list.append(mysqldump_cron)

  def installDevelopmentEnvironment(self):
    ca_conf = self.installCertificateAuthority()
    memcached_conf = self.installMemcached(ip=self.getLocalIPv4Address(),
        port=11000)
    conversion_server_conf = self.installConversionServer(
        self.getLocalIPv4Address(), 23000, 23060)
    mysql_conf = self.installMysqlServer(self.getLocalIPv4Address(), 45678,
        template_filename=pkg_resources.resource_filename(__name__,
          'template/my.cnf.in'), parallel_test_database_amount=10,
          mysql_conf=dict(innodb_buffer_pool_size='1G'), with_backup=False)
    self.installMysqldumpBackup()
    kumo_conf = self.installKumo(self.getLocalIPv4Address())
    user, password = self.installERP5()
    self.installTestRunner(ca_conf, mysql_conf, conversion_server_conf,
        memcached_conf, kumo_conf)
    self.installTestSuiteRunner(ca_conf, mysql_conf, conversion_server_conf,
                           memcached_conf, kumo_conf)
    ip = self.getLocalIPv4Address()
    zope_port = '18080'
    zodb_dir = os.path.join(self.data_root_directory, 'zodb')
    self._createDirectory(zodb_dir)
    zodb_root_path = os.path.join(zodb_dir, 'root.fs')
    self.installZope(ip, zope_port, 'zope_development',
        zodb_configuration_string=self.substituteTemplate(
          self.getTemplateFilename('zope-zodb-snippet.conf.in'),
          dict(zodb_root_path=zodb_root_path)),
          thread_amount=8, with_timerservice=True,
          zope_environment=dict(TZ=BEF_TIMEZONE))
    self.setConnectionDict(dict(
      site_user=user,
      site_password=password,
      memcached_url=memcached_conf['memcached_url'],
      kumo_url=kumo_conf['kumo_address'],
      conversion_server_url='%(conversion_server_ip)s:%(conversion_server_port)s' %
        conversion_server_conf,
      # openssl binary might be removed, as soon as CP environment will be
      # fully controlled
      openssl_binary=self.options['openssl_binary'],
      # As soon as there would be Vifib ERP5 configuration and possibility to
      # call it over the network this can be removed
      certificate_authority_path=ca_conf['certificate_authority_path'],
      # as installERP5Site is not trusted (yet) and this recipe is production
      # ready expose more information
      mysql_url='%(mysql_database)s@%(ip)s:%(tcp_port)s %(mysql_user)s %(mysql_password)s' % mysql_conf,
      development_zope='http://%s:%s/' % (ip, zope_port)
    ))
    return self.path_list

  def installBT5Repo(self):
    """
    Create read only repo in the partition, to ease ERP5 configuration
    """
    repo_path = os.path.join(self.var_directory, "bt5repo")
    if not os.path.isdir(repo_path):
      os.mkdir(repo_path)
    for repo in self.options.get('bt5_repo_list', '').splitlines():
      if not repo:
        continue
      target, linkname = repo.split()
      link = os.path.join(repo_path, linkname)
      if os.path.lexists(link):
        if not os.path.islink(link):
          raise zc.buildout.UserError(
              'Target link already %r exists but it is not link' % link)
        os.unlink(link)
      os.symlink(target, link)
      self.logger.debug('Created link %r -> %r' % (link, target))
    self.path_list.append(repo_path)

  def _install(self):
    self.path_list = []
    self.requirements, self.ws = self.egg.working_set()
    # self.cron_d is a directory, where cron jobs can be registered
    self.cron_d = self.installCrond()
    self.logrotate_d, self.logrotate_backup = self.installLogrotate()
    self.killpidfromfile = zc.buildout.easy_install.scripts(
        [('killpidfromfile', 'slapos.recipe.erp5.killpidfromfile',
          'killpidfromfile')], self.ws, sys.executable, self.bin_directory)[0]
    self.path_list.append(self.killpidfromfile)
    self.linkBinary()
    self.installBT5Repo()
    if self.parameter_dict.get('production_mysql', 'false').lower() == 'true':
      self.development = False
      return self.installProductionMysql()
    elif self.parameter_dict.get(
        'production_application', 'false').lower() == 'true':
      self.development = False
      return self.installProductionApplication()
    elif self.parameter_dict.get(
        'production_frontend', 'false').lower() == 'true':
      self.development = False
      return self.installProductionFrontend()
    elif self.parameter_dict.get('development', 'true').lower() == 'true':
      self.development = True
      return self.installDevelopmentEnvironment()
    else:
      raise NotImplementedError('Flavour of instance have to be given.')