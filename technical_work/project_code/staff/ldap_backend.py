from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, core
from django.contrib.auth.models import User
import re, string
from django.utils.translation import ugettext as _
from django.contrib import messages

class LDAPBackend():
    def authenticate(self, request, username=None, password=None):
        dn = "uid=" + username + ",ou=People,dc=dcs,dc=aber,dc=ac,dc=uk"
        try:
            #connect to server via ldap
            server = Server('ldap.dcs.aber.ac.uk', get_info=ALL, port=636, use_ssl=True, connect_timeout=5)
            conn = Connection(server, dn, password, auto_bind=True)

            #search for the entry reperesenting the logged in user
            conn.search(dn, '(objectClass=*)', attributes=ALL_ATTRIBUTES)
            if len(conn.entries) != 1:
                raise RuntimeError('Expected one entry, found {}!'.format(len(conn.entries)))
            entry = conn.entries[0]
            print(entry)

            #extarct the part of the gecos field we are interested in
            gecos = "[????]"
            mail = ""
            forename = ""
            surname = ""
            for line in str(entry).splitlines():
                if re.search("^gecos:", line.strip()):
                    gecos = line.strip()[-6:]
                    forename = line.strip().split(" ")[1]
                elif re.search("^mail:", line.strip()):
                    mail = line.strip().split("mail: ",1)[1]
                elif re.search("^sn:", line.strip()):
                    surname = line.strip().split("sn: ",1)[1]

            #display user role
            if gecos[-3:]=="SM]":
                print("User is Staff: gecos=" + gecos)
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    #create a new user
                    user = User(username=username, first_name=forename, last_name=surname, email=mail)
                    user.save()
                return user
            elif gecos[-3:]=="UG]":
                print("User is Undergraduate: gecos=" + gecos)
                #return None
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    #create a new user
                    user = User.objects.create(username=username, first_name=forename, last_name=surname, email=mail)
                return user
            elif gecos=="[????]":
                print("Gecos field could not be found")
                return None
            else:
                print("User is Other: gecos=" + gecos)
                return None
        except core.exceptions.LDAPBindError as e:
            #LDAP bind failure perhaps due to authentication error
            print("LDAP bind failure perhaps due to authentication error") #should be log messages
            messages.error(request, _('LDAP bind failure perhaps due to authentication error'))
            return None
        except core.exceptions.LDAPSocketOpenError as e:
            #server did not respond - cannot find server probably because not on univerity network
            print("Failed to open socket to server probably becasue not on univerity network")
            messages.error(request, _('Failed to open socket to server probably becasue not on univerity network'))
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None
