apache_frontend
===============

Frontend system using Apache, allowing to rewrite and proxy URLs like
myinstance.myfrontenddomainname.com to real IP/URL of myinstance.

apache_frontend works using the master instance / slave instance design.
It means that a single main instance of Apache will be used to act as frontend
for many slaves.


How to use
==========

First, you will need to request a "master" instance of Apache Frontend with
"domain" parameter, like::
  <?xml version='1.0' encoding='utf-8'?>
  <instance>
   <parameter id="domain">moulefrite.org</parameter>
   <parameter id="port">443</parameter>
  </instance>

Then, it is possible to request many slave instances
(currently only from slapconsole, UI doesn't work yet)
of Apache Frontend, like::
  instance = request(
    software_release=apache_frontend,
    partition_reference='frontend2',
    shared=True,
    partition_parameter_kw={"url":"https://[1:2:3:4]:1234/someresource"}
  )
Those slave instances will be redirected to the "master" instance,
and you will see on the "master" instance the associated RewriteRules of
all slave instances.

Finally, the slave instance will be accessible from:
https://someidentifier.moulefrite.org.

Instance Parameters
===================

Master Instance Parameters
--------------------------

domain
~~~~~~
name of the domain to be used (example: mydomain.com). Subdomains of this
domain will be used for the slave instances (example:
instance12345.mydomain.com). It is then recommended to add a wildcard in DNS
for the subdomains of the chosen domain like::
  *.mydomain.com. IN A 123.123.123.123
Using the IP given by the Master Instance.
"domain" is a mandatory Parameter.

port
~~~~
Port used by Apache. Optional parameter, defaults to 4443.

plain_http_port
Port used by apache to serve plain http (only used to redirect to https).
Optional parameter, defaults to 8080.

Slave Instance Parameters
-------------------------

url
~~~
url of backend to use.
"url" is a mandatory parameter.
Example: http://mybackend.com/myresource

cache
~~~~~
Specify if slave instance should use a varnish / stunnel to connect to backend.
Possible values: "true", "false".
"cache" is an optional parameter. Defaults to "false". 
Example: true

type
~~~~
Specify if slave instance will redirect to a zope backend. If specified, Apache
RewriteRule will use Zope's Virtual Host Daemon.
Possible values: "zope", "default".
"type" is an optional parameter. Defaults to "default". 
Example: zope

custom_domain
~~~~~~~~~~~~~
Domain name to use as frontend. The frontend will be accessible from this domain.
"custom_domain" is an optional parameter. Defaults to
[instancereference].[masterdomain]. 
Example: www.mycustomdomain.com


Advanced example
================

Request slave frontend instance using a Zope backend, with Varnish activated,
listening to a custom domain::
  instance = request(
    software_release=apache_frontend,
    partition_reference='frontend2',
    shared=True,
    partition_parameter_kw={
        "url":"https://[1:2:3:4]:1234/someresource",
        "cache":"true",
        "type":"zope",
        "custom_domain":"mycustomdomain.com",
    }
  )

Notes
=====

It is not possible with slapos to listen to port <= 1024, because process are
not run as root. It is a good idea then to go on the node where the instance is
and set some iptables rules like (if using default ports)::
  iptables -t nat -A PREROUTING -p tcp -d {public ip} --dport 443 -j DNAT --to-destination {listening ip}:4443
  iptables -t nat -A PREROUTING -p tcp -d {public_ip} --dport 80 -j DNAT --to-destination {listening ip}:8080
