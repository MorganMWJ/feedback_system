from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, core
import re, string

#get login details
uid = input("Enter username: ")
password = input("Enter password: ")
dn = "uid=" + uid + ",ou=People,dc=dcs,dc=aber,dc=ac,dc=uk"


try:
    #connect to server via ldap
    server = Server('ldap.dcs.aber.ac.uk', get_info=ALL, port=636, use_ssl=True)
    conn = Connection(server, dn, password, auto_bind=True)
    print('done')

    #search for the entry reperesenting the logged in user
    conn.search(dn, '(objectClass=*)', attributes=ALL_ATTRIBUTES)
    if len(conn.entries) != 1:
        raise RuntimeError('Expected one entry, found {}!'.format(len(conn.entries)))
    entry = conn.entries[0]
    print(entry)

    #extarct the part of the gecos field we are interested in
    gecos = None
    for line in str(entry).splitlines():
        if re.search("^gecos", line.strip()):
            gecos = line.strip()[-6:]

    #display user role
    if gecos[-3:]=="SM]":
        print("User is Staff: gecos=" + gecos)
    elif gecos[-3:]=="UG]":
        print("User is Undergraduate: gecos=" + gecos)  
    else:
        print("User is Other: gecos=" + gecos)

        
except core.exceptions.LDAPBindError as e:
    #LDAP bind failure (perhaps due to authentication error)
    print('LDAP Bind Failed: ', e) 




################################################################################

#Distinquished Name uid=mwj7,ou=People,dc=dcs,dc=aber,dc=ac,dc=uk
#we dont want a clear text connection we want a secure/encrypted one
#therefore we are using LDAP over TLS (port 636)

#print(server.info)
#print(conn.extend.standard.who_am_i())
#print(conn)
#below code is error with search filter
#print(conn.search(search_base='ou=People', search_filter='gecos=*'))
#conn.start_tls()
#print(server.schema)
#print(conn.response)
