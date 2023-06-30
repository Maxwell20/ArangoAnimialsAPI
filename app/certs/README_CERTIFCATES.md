
# openssl step and cmd used to create test certificates.


# You can use certs as is and you can even use the clientcert 
# but the client cert is cstringer. 
# !!! To create your own user cert go to step 3.  


# Create Certs
# on windows you will need cygwin with openssl to create needed certs 
# example of change to need dir /cygdrive/c is C:/  
# cd /cygdrive/c/PROJECTS/RockProject/proxy/test-certs
# 
# on linux should be as easy as yum install openssl 
#
# Cmds and steps to create needed certificates
#
# step 1: Create the CA
	  openssl req -config ./openssl.cnf -newkey rsa:2048 -nodes -keyform PEM -keyout ca.key -x509 
	  -days 3650 -extensions certauth -outform PEM -out ca.cer
#
# step 2: Create server certs 3 sub steps 
#   Generate private SSL key for the server:
	openssl genrsa -out server.key 2048
# *note to view: openssl rsa -noout -text -check -in server.key


#   Generate Certificate Signing Request in PKCS#10 format
  openssl req -config ./openssl.cnf -new -key server.key -out server.req
# *note to view: openssl req -noout -text -verify -in server.req

#   Sign server cert with certificate authority (CA) 
   openssl x509 -req -in server.req -CA ca.cer -CAkey ca.key -set_serial 100 -extfile openssl.cnf 
       -extensions server -days 365 -outform PEM -out server.cer
# *note to view: openssl x509 -noout -text -in server.cer
#
# step 3: Create client certs 3 sub steps
#   Generete private key for SSL client 
       openssl genrsa -out client.key 2048
# *note to view: openssl rsa -noout -text -check -in client.key

#   Generate Certificate Signing Request for user cert
       openssl req -config ./openssl.cnf -new -key client.key -out client.req
# *note to view: openssl req -noout -text -verify -in client.req

#   Sign client cert with certificate authority (CA)
       openssl x509 -req -in client.req -CA ca.cer -CAkey ca.key -set_serial 101 -extfile openssl.cnf 
           -extensions client -days 365 -outform PEM -out client.cer
# *note to view: openssl x509 -noout -text -in client.cer


#   Save client’s private key and certificate in a PKCS#12 format needed
#   to import the certificate into the web browser’s certificate manager.
#   will ask for password just for testing use 1234 
#       openssl pkcs12 -export -inkey client.key -in client.cer -out client.p12
#

IMPORTANT

# if windows add this to hosts file
# C:\Windows\System32\drivers\etc\hosts
------------
# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost
127.0.0.1 localhostdomain.com
127.0.0.1 localhost
127.0.0.1 www.localhostdomain.com


# In web browser go to setting search for cert manager
# 1. Import client certs
# In chrome in search cer "manage device certificate"
#   click import cert. point to client.p12. import as client cert.
#   If you use the provided client.p12 the password is 1234
# 2. Import CA cert
#   click import cert. point to ca.cer. import as Trusted Root cert.
# next test out the site should ask for client cert and be https/ssl enable.
# and new url will be https://www.localhostdomain.com/ after logging in.

