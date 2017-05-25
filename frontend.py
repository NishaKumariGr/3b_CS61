from pymongo import MongoClient
import pprint
import sys                                   # for misc errors
import cmd                                   # for creating line-oriented command processors
import shlex
 # db server to connect to
SERVER = "mongodb://Team01:7IXQg4KMgmwqeKgS@cluster0-shard-00-00-ppp7l.mongodb.net:27017,cluster0-shard-00-01-ppp7l.mongodb.net:27017,cluster0-shard-00-02-ppp7l.mongodb.net:27017"               

class command_Line_Interact(cmd.Cmd):
    """Command processor"""
    def do_register(self, line):
    	


#main function where the connection happens
if __name__ == "__main__":
	con = MongoClient(SERVER, connect = False, ssl = True)
	con.server_info()
	print("Connection to MegaMongododo Publications DB established.")
	db = con['Team01DB']
	com_intr = command_Line_Interact()
	com_intr.cmdloop()