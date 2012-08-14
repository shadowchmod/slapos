from setuptools import setup, find_packages
import glob
import os

version = '0.59-dev'
name = 'slapos.cookbook'
long_description = open("README.txt").read() + "\n" + \
    open("CHANGES.txt").read() + "\n"

for f in sorted(glob.glob(os.path.join('slapos', 'recipe', 'README.*.txt'))):
  long_description += '\n' + open(f).read() + '\n'

# extras_requires are not used because of
#   https://bugs.launchpad.net/zc.buildout/+bug/85604
setup(name=name,
      version=version,
      description="SlapOS recipes.",
      long_description=long_description,
      classifiers=[
          "Framework :: Buildout :: Recipe",
          "Programming Language :: Python",
        ],
      keywords='slapos recipe',
      license='GPLv3',
      namespace_packages=['slapos', 'slapos.recipe'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'PyXML', # for full blown python interpreter
        'lxml', # for full blown python interpreter
        'netaddr', # to manipulate on IP addresses
        'setuptools', # namespaces
        'inotifyx', # to watch filesystem changes (used in lockfile)
        'slapos.core', # uses internally
#        'slapos.toolbox', # needed for libcloud, cloudmgr, disabled for now
        'xml_marshaller', # need to communication with slapgrid
        'zc.buildout', # plays with buildout
        'zc.recipe.egg', # for scripts generation
        ],
      zip_safe=True,
      entry_points={
        'zc.buildout': [
          'agent = slapos.recipe.agent:Recipe',
          'apache.frontend = slapos.recipe.apache_frontend:Recipe',
          'apachephp = slapos.recipe.apachephp:Recipe',
          'apacheproxy = slapos.recipe.apacheproxy:Recipe',
          'apache.zope.backend = slapos.recipe.apache_zope_backend:Recipe',
          'certificate_authority = slapos.recipe.certificate_authority:Recipe',
          'certificate_authority.request = slapos.recipe.certificate_authority:Request',
          'check_port_listening = slapos.recipe.check_port_listening:Recipe',
          'check_url_available = slapos.recipe.check_url_available:Recipe',
          'cloud9 = slapos.recipe.cloud9:Recipe',
          'cron = slapos.recipe.dcron:Recipe',
          'cron.d = slapos.recipe.dcron:Part',
          'davstorage = slapos.recipe.davstorage:Recipe',
          'dropbear = slapos.recipe.dropbear:Recipe',
          'dropbear.add_authorized_key = slapos.recipe.dropbear:AddAuthorizedKey',
          'dropbear.client = slapos.recipe.dropbear:Client',
          'duplicity = slapos.recipe.duplicity:Recipe',
          'erp5scalabilitytestbed = slapos.recipe.erp5scalabilitytestbed:Recipe',
          'equeue = slapos.recipe.equeue:Recipe',
          'erp5testnode = slapos.recipe.erp5testnode:Recipe',
          'generate.mac = slapos.recipe.generatemac:Recipe',
          'generate.password = slapos.recipe.generatepassword:Recipe',
          'nbdserver = slapos.recipe.nbdserver:Recipe',
          'onetimeupload = slapos.recipe.onetimeupload:Recipe',
          'helloworld = slapos.recipe.helloworld:Recipe',
          'generic.cloudooo = slapos.recipe.generic_cloudooo:Recipe',
          'cloudooo.test = slapos.recipe.cloudooo_test:Recipe',
          'firefox = slapos.recipe.firefox:Recipe',
          'fontconfig = slapos.recipe.fontconfig:Recipe',
          'java = slapos.recipe.java:Recipe',
          'kumofs = slapos.recipe.kumofs:Recipe',
          'kvm = slapos.recipe.kvm:Recipe',
          'kvm.frontend = slapos.recipe.kvm_frontend:Recipe',
          'generic.kumofs = slapos.recipe.generic_kumofs:Recipe',
          'haproxy = slapos.recipe.haproxy:Recipe',
          'libcloud = slapos.recipe.libcloud:Recipe',
          'libcloudrequest = slapos.recipe.libcloudrequest:Recipe',
          'lockfile = slapos.recipe.lockfile:Recipe',
          'memcached = slapos.recipe.memcached:Recipe',
          'generic.memcached = slapos.recipe.generic_memcached:Recipe',
          'mysql = slapos.recipe.mysql:Recipe',
          'mydumper = slapos.recipe.mydumper:Recipe',
          'generic.mysql = slapos.recipe.generic_mysql:Recipe',
          'mkdirectory = slapos.recipe.mkdirectory:Recipe',
          'nosqltestbed = slapos.recipe.nosqltestbed:NoSQLTestBed',
          'notifier = slapos.recipe.notifier:Recipe',
          'notifier.callback = slapos.recipe.notifier:Callback',
          'notifier.notify = slapos.recipe.notifier:Notify',
          'novnc = slapos.recipe.novnc:Recipe',
          'lamp = slapos.recipe.lamp:Request',
          'lamp.request = slapos.recipe.lamp:Request',
          'lamp.static = slapos.recipe.lamp:Static',
          'lamp.simple = slapos.recipe.lamp:Simple',
          'logrotate = slapos.recipe.logrotate:Recipe',
          'logrotate.d = slapos.recipe.logrotate:Part',
          'pbs = slapos.recipe.pbs:Recipe',
          'publish = slapos.recipe.publish:Recipe',
          'publishurl = slapos.recipe.publishurl:Recipe',
          'pwgen = slapos.recipe.pwgen:Recipe',
          'pwgen.stable = slapos.recipe.pwgen:StablePasswordGeneratorRecipe',
          'proactive = slapos.recipe.proactive:Recipe',
          'request = slapos.recipe.request:Recipe',
          'seleniumrunner = slapos.recipe.seleniumrunner:Recipe',
          'sheepdogtestbed = slapos.recipe.sheepdogtestbed:SheepDogTestBed',
          'shell = slapos.recipe.shell:Recipe',
          'shellinabox = slapos.recipe.shellinabox:Recipe',
          'slapconfiguration = slapos.recipe.slapconfiguration:Recipe',
          'symbolic.link = slapos.recipe.symbolic_link:Recipe',
          'softwaretype = slapos.recipe.softwaretype:Recipe',
          'siptester = slapos.recipe.siptester:SipTesterRecipe',
          'simplelogger = slapos.recipe.simplelogger:Recipe',
          'slaprunner = slapos.recipe.slaprunner:Recipe',
          'slapmonitor = slapos.recipe.slapmonitor:Recipe',
          'slapreport = slapos.recipe.slapreport:Recipe',
          'sshkeys_authority = slapos.recipe.sshkeys_authority:Recipe',
          'sshkeys_authority.request = slapos.recipe.sshkeys_authority:Request',
          'sphinx= slapos.recipe.sphinx:Recipe',
          'stunnel = slapos.recipe.stunnel:Recipe',
          'testnode = slapos.recipe.testnode:Recipe',
          'urlparse = slapos.recipe._urlparse:Recipe',
          'vifib = slapos.recipe.vifib:Recipe',
          'waitfor = slapos.recipe.waitfor:Recipe',
          'xvfb = slapos.recipe.xvfb:Recipe',
          'xwiki = slapos.recipe.xwiki:Recipe',
          'zabbixagent = slapos.recipe.zabbixagent:Recipe',
          'generic.zope = slapos.recipe.generic_zope:Recipe',
          'generic.zope.zeo.client = slapos.recipe.generic_zope_zeo_client:Recipe',
          'zeo = slapos.recipe.zeo:Recipe',
          'tidstorage = slapos.recipe.tidstorage:Recipe',
          'erp5.bootstrap = slapos.recipe.erp5_bootstrap:Recipe',
          'erp5.promise = slapos.recipe.erp5_promise:Recipe',
          'erp5.update = slapos.recipe.erp5_update:Recipe',
          'erp5.test = slapos.recipe.erp5_test:Recipe',
          'generic.varnish = slapos.recipe.generic_varnish:Recipe',
          'webchecker = slapos.recipe.web_checker:Recipe',
          'signalwrapper= slapos.recipe.signal_wrapper:Recipe',
        ],
        'slapos.recipe.nosqltestbed.plugin': [
          'kumo = slapos.recipe.nosqltestbed.kumo:KumoTestBed',
        ],
      },
    )
