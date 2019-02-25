from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, core
from django.contrib.auth.models import Permission, User
import re, string

class LDAPBackend():
    def authenticate(self, request, username=None, password=None):
        dn = "uid=" + username + ",ou=People,dc=dcs,dc=aber,dc=ac,dc=uk"
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
            gecos = "[????]"
            for line in str(entry).splitlines():
                if re.search("^gecos", line.strip()):
                    gecos = line.strip()[-6:]
                    tempResult = line.strip()

            #display user role
            if gecos[-3:]=="SM]":
                print("User is Staff: gecos=" + gecos)
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    #create a new user
                    user = User(username=username) #todo could add email,first,last name from gecos field
                    user.save()
                return user
            elif gecos[-3:]=="UG]":
                print("User is Undergraduate: gecos=" + gecos)
                #return None
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    #create a new user
                    user = User(username=username) #todo could add email,first,last name from gecos field
                    user.save()
                return user
            elif gecos=="[????]":
                print("Gecos field could not be found")
                return None
            else:
                print("User is Other: gecos=" + gecos)
                return None
        except core.exceptions.LDAPBindError as e:
            #LDAP bind failure perhaps due to authentication error
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
