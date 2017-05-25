from pymongo import MongoClient
import pprint
import sys                                   # for misc errors
import cmd                                   # for creating line-oriented command processors
import shlex

#7IXQg4KMgmwqeKgS
 # db server to connect to
SERVER = "mongodb://Team01:7IXQg4KMgmwqeKgS@cluster0-shard-00-00-ppp7l.mongodb.net:27017,cluster0-shard-00-01-ppp7l.mongodb.net:27017,cluster0-shard-00-02-ppp7l.mongodb.net:27017"               

class command_Line_Interact(cmd.Cmd):
    """Command processor"""
    def do_register(self, line):
    	tokens = shlex.split(line)
    	if tokens[0] == "AUTHOR":
    		auth_doc = {"FirstName":tokens[1],"LastName":tokens[2], "MiddleName":None, "EmailAddress":tokens[3], "MailingAddress":tokens[4], "Affiliation":None}
    		db.AUTHOR.insert(auth_doc)
    	elif tokens[0] == "EDITOR":
    		ed_doc = {"FirstName":tokens[1],"LastName":tokens[2], "MiddleName":None}
    		db.EDITOR.insert(ed_doc)
    	elif tokens[0] == "REVIEWER":
    		lenOfList=len(tokens)
    		if lenOfList==4:
    			rev_doc = {"FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":None, "RICode3":None,"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)
    		elif lenOfList==5:
    			rev_doc = {"FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":tokens[4], "RICode3":None,"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)
    		elif lenOfList==6:
    			rev_doc = {"FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":tokens[4], "RICode3":tokens[5],"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)

    	cursor = db.AUTHOR.find({})
    	for document in cursor: 
			pprint.pprint(document)

    	


#main function where the connection happens
if __name__ == "__main__":
	con = MongoClient(SERVER, connect = False, ssl = True)
	con.server_info()
	print("Connection to MegaMongododo Publications DB established.")
	db = con['Team01DB']
	com_intr = command_Line_Interact()
	com_intr.cmdloop()