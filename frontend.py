from pymongo import MongoClient
import pprint
import sys                                   # for misc errors
import cmd                                   # for creating line-oriented command processors
import shlex

#./mongo "mongodb://cluster0-shard-00-00-ppp7l.mongodb.net:27017,cluster0-shard-00-01-ppp7l.mongodb.net:27017,cluster0-shard-00-02-ppp7l.mongodb.net:27017/Team01DB?replicaSet=Cluster0-shard-0" --authenticationDatabase admin --ssl --username Team01 --password
#7IXQg4KMgmwqeKgS 
# db server to connect to
SERVER = "mongodb://Team01:7IXQg4KMgmwqeKgS@cluster0-shard-00-00-ppp7l.mongodb.net:27017,cluster0-shard-00-01-ppp7l.mongodb.net:27017,cluster0-shard-00-02-ppp7l.mongodb.net:27017"               

class command_Line_Interact(cmd.Cmd):
    """Command processor""" 
    def do_exit(self, line):
    	return True

    def do_typeset(self, line):
		tokens = shlex.split(line)
		manu_id = tokens[0]
		pages = tokens[1]
		#check if editor can manage this manuscript
		cursorE = db.MANUSCRIPT.aggregate([
			{"$match":{
				"_id":manu_id
			}},
			{"$project":{
				"EDITOR_idEDITOR":1,
				"_id":0
			}}
		])
		for document in cursorE: 
			if document['EDITOR_idEDITOR'] == self.id:
				print("This Editor has the authorization to assign this manuscipt!")
				# check if manuscript has the appropriate status
				cursorM = db.MANUSCRIPT.aggregate([
					{"$match":{
						"_id":manu_id
					}},
					{"$project":{
						"Status": 1,
						"_id":0
					}}
				])
				for doc in cursorM:
					m_stat = doc['Status']
					if m_stat == "Accepted":
						print("This manuscript has the appropriate current status to be typeset!")
						#update status and pages
						db.MANUSCRIPT.update( 
							{"_id": manu_id, "EDITOR_idEDITOR" : self.id},
							{ "$set":{"Status": "Typeset", "Pages": pages}},
						upsert=True )
						print("Manuscript "+ manu_id+ "'s number of pages set to "+ pages+ ".")
					else:
						print("Manuscript DOES NOT have the appropriate current status for this action!")

			else:
				print("This Editor DOES NOT have the authorization to assign this manuscipt! Try again.") 

    def do_RETRACT(self,line):
    	response = raw_input ("Are you sure? (yes/no) \n")
    	print (line)
    	if response=="yes":
    		db.ManuscriptsInIssue.remove({"ManuscriptID":line})
    		db.AUTHORSINMANUSCRIPT.remove({"ManuscriptID":line})
    		db.REVIEW.remove({"ManuscriptID":line})
    		db.MANUSCRIPT.remove({ "_id" : line})
    		print("Manuscript "+ line +" is deleted from the system!")

    def do_submit(self,line):
    	tokens = shlex.split(line)
        title = tokens[0]
        Affiliation = tokens[1]
        RICode = tokens[2]
        sec_authors = tokens[3:-1] 
        filename = tokens[-1]
        latest_man = db.MANUSCRIPT.find()
        for doc in latest_man:
        	latest_id = doc['_id']
        newid = int(latest_id)+1
        #Submit the manuscript
        sub_man = {"_id":str(newid), "RICode":RICode, "EDITOR_idEDITOR":"1", "Title":title, "Status":"Received", "FileBlob":filename, "Pages":None, "Acceptant_RejectionDate":None, "IssueYear":None, "IssueVolume":None}
        db.MANUSCRIPT.insert(sub_man)
    	msg = "Manuscript has been submitted in the system! The ID of the new Manuscript is: {0}".format(newid)
        print(msg)

        #Update the affiliation of the author
        db.AUTHOR.update(
        	{"_id":self.id},
        	{"$set":{"Affiliation": Affiliation}},
        upsert=True)

        #Update all the the authors in AUTHORSINMANUSCRIPT table for credits' record
        a_rank = 2
        man_auth_first = {"ManuscriptID":str(newid), "AuthorID":self.id, "AuthorPlace": "1"}
        db.AUTHORSINMANUSCRIPT.insert(man_auth_first)
        for auth in sec_authors:
        	man_auth_other = {"ManuscriptID":str(newid), "AuthorID":auth, "AuthorPlace": str(a_rank)}
        	db.AUTHORSINMANUSCRIPT.insert(man_auth_other)
        	a_rank += 1
    	
    def do_assign(self, line):
		tokens = shlex.split(line)
		manu_id = tokens[0]
		rev_id = tokens[1]
		cursorE = db.MANUSCRIPT.aggregate([
			{"$match":{
				"_id":manu_id
			}},
			{"$project":{
				"EDITOR_idEDITOR":1,
				"_id":0
			}}
		])
		for document in cursorE: 
			if document['EDITOR_idEDITOR'] == self.id:
				print("This Editor has the authorization to assign this manuscipt!")
				rev_assign = {"REVIEWER_idREVIEWER":rev_id,"EDITOR_idEDITOR":self.id, "ManuscriptID":manu_id, "Clarity":None, "Methodology":None, "Contribution":None,"PublicationRecommendation":None, "Appropriateness":None} 
				db.REVIEW.insert(rev_assign)
				#print(rev_assign)
				print("Reviewer Successfully Assigned!") 
				break
			else:
				print("This Editor DOES NOT have the authorization to assign this manuscipt! Try again.") 

    def do_login (self, line):
    	#still have to order by status!!!
		self.id= line[1:]

		if line[0]=="A":
			self.table="AUTHOR"
			print("Welcome Author "+ line)
			print("Here are your details:")
			cursorA = db.AUTHOR.aggregate([
				{"$match":{
					"_id":self.id
				}},
				{"$project":{
					"FirstName":1,
					"LastName":1,
					"MailingAddress":1,
					"_id":0
				}}
			])
			for document in cursorA: 
				pprint.pprint(document)

			print(" ")
			print("Your current manuscript details: ")
			cursorA2 = db.MANUSCRIPT.aggregate([
				{"$lookup":{
					"from": "AUTHORSINMANUSCRIPT", 
					"localField": "_id", 
					"foreignField": "ManuscriptID", 
					"as": "authorsMans"
				}},
				{"$unwind":"$authorsMans"},
				{"$match":{
					"$and":[
						{"authorsMans.AuthorID":self.id},
						{"authorsMans.AuthorPlace":"1"}
					]
				}},
				{"$project":{
					"_id":1,
					"Status":1
				}}
			])
			for document in cursorA2: 
				pprint.pprint(document)

		elif line[0]=="E":
			self.table="EDITOR"
			print("Welcome Editor "+ line)
			print("Here are your details:")
			cursorE = db.EDITOR.aggregate([
				{"$match":{
					"_id":self.id
				}},
				{"$project":{
					"FirstName":1,
					"LastName":1,
					"_id":0
				}}
			])
			for document in cursorE: 
				pprint.pprint(document)

			print(" ")
			print("Your current manuscript details: ")
			cursorE2 = db.MANUSCRIPT.aggregate([{"$match":{"EDITOR_idEDITOR" : self.id}}, {"$sort": {"_id":1}}])
			for document in cursorE2: 
				pprint.pprint(document)


		elif line[0]=="R":
			self.table="REVIEWER"
			print("Welcome Reviewer "+ line)
			print("Here are your details:")
			cursorR = db.REVIEWER.aggregate([
				{"$match":{
					"_id":self.id
				}},
				{"$project":{
					"FirstName":1,
					"LastName":1,
					"_id":0
				}}
			])
			for document in cursorR: 
				pprint.pprint(document)
			
			print(" ")
			print("Your current manuscript details: ")
			cursorR2 = db.MANUSCRIPT.aggregate([
				{"$lookup":{
					"from": "REVIEW", 
					"localField": "_id", 
					"foreignField": "ManuscriptID", 
					"as": "reviewMans"
				}},
				{"$unwind":"$reviewMans"},
				{"$match":{
					"reviewMans.REVIEWER_idREVIEWER":self.id
				}},
				{"$project":{
					"_id":1,
					"Status":1
				}}
			])
			for document in cursorR2: 
				pprint.pprint(document)
		print_options(self.table)

    def do_STATUS (self, line):
    	#have to sort by status in editor
		if self.table == "AUTHOR":		
			cursor = db.MANUSCRIPT.aggregate([
				{"$lookup":{
					"from": "AUTHORSINMANUSCRIPT", 
					"localField": "_id", 
					"foreignField": "ManuscriptID", 
					"as": "authorsMans"
				}},
				{"$unwind":"$authorsMans"},
				{"$match":{
					"$and":[
						{"authorsMans.AuthorID":self.id},
						{"authorsMans.AuthorPlace":"1"}
					]
				}},
				{"$project":{
					"authorsMans":0
				}}
			])
			for document in cursor: 
				pprint.pprint(document)

		elif self.table == "EDITOR":	
		#order by status!!
			cursor1 = db.MANUSCRIPT.aggregate([{"$match":{"EDITOR_idEDITOR" : self.id}}, {"$sort": {"_id":1}}])
			for document in cursor1: 
				pprint.pprint(document)

		elif self.table == "REVIEWER":
			cursor2 = db.MANUSCRIPT.aggregate([
				{"$lookup":{
					"from": "REVIEW", 
					"localField": "_id", 
					"foreignField": "ManuscriptID", 
					"as": "reviewMans"
				}},
				{"$unwind":"$reviewMans"},
				{"$match":{
					"reviewMans.REVIEWER_idREVIEWER":self.id
				}},
				{"$project":{
					"_id":1,
					"Status":1
				}}
			])
			for document in cursor2: 
				pprint.pprint(document)

    def do_register(self, line):
    	tokens = shlex.split(line)
    	if tokens[0] == "AUTHOR":
    		latest_auth = db.AUTHOR.find()
    		for doc in latest_auth:
    			latest_id = doc['_id']

    		newid = int(latest_id)+1
    		auth_doc = {"_id": str(newid), "FirstName":tokens[1],"LastName":tokens[2], "MiddleName":None, "EmailAddress":tokens[3], "MailingAddress":tokens[4], "Affiliation":None}
    		db.AUTHOR.insert(auth_doc)

    	elif tokens[0] == "EDITOR":
    		latest_ed = db.EDITOR.find()
    		for doc in latest_ed:
    			latest_id = doc['_id']

    		newid = int(latest_id)+1
    		ed_doc = {"_id": str(newid), "FirstName":tokens[1],"LastName":tokens[2], "MiddleName":None}
    		db.EDITOR.insert(ed_doc)
    	elif tokens[0] == "REVIEWER":
    		lenOfList=len(tokens)
    		latest_rev = db.REVIEWER.find()
    		for doc in latest_rev:
    			latest_id = doc['_id']

    		newid = int(latest_id)+1
    		if lenOfList==4:
    			rev_doc = {"_id": str(newid), "FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":None, "RICode3":None,"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)
    		elif lenOfList==5:
    			rev_doc = {"_id": str(newid), "FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":tokens[4], "RICode3":None,"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)
    		elif lenOfList==6:
    			rev_doc = {"_id": str(newid), "FirstName":tokens[1],"EmailId":None, "Affiliation":None, "RICode1":tokens[3], "RICode2":tokens[4], "RICode3":tokens[5],"LastName":tokens[2], "MiddleName":None} 
    			db.REVIEWER.insert(rev_doc)

    def do_resign(self,line):
    	print ("Welcome "+line)
    	db.REVIEW.remove({ "REVIEWER_idREVIEWER" : line[1:]})
    	db.REVIEWER.remove({ "_id" : line[1:]})
    	print ("Thank you for your service")

    def do_REVIEWREJECT(self,line):
    	tokens = shlex.split(line)

    	#check if the reviewer can review this manuscript 
    	ids = db.REVIEW.find({"REVIEWER_idREVIEWER":self.id},{"ManuscriptID":1, "_id":0})
    	flag = 0
    	for doc in ids:
    		latest_id = doc['ManuscriptID']
    		if latest_id==tokens[0]:
    			flag=1


    	if flag ==1:
	   	status = db.MANUSCRIPT.find({"_id": tokens[0]},{"Status":1, "_id":0})
	    	for doc in status:
	    		latest_status = doc['Status']

	    	print (latest_status)
	    	# check if the status of given manuscript is "Under review"
	    	if latest_status=="Under review":
		    	db.REVIEW.update( 
						{"ManuscriptID": tokens[0], "REVIEWER_idREVIEWER" : self.id},
						{ "$set":{"PublicationRecommendation": "Reject", "Clarity": tokens[1], "Methodology": tokens[2], "Contribution": tokens[3], "Appropriateness": tokens[4]} },
						upsert=True )
		    	print ("Updated publication recommendation  to rejected")
		else:
		 	print ("Cannot review this manuscript, not assigned for reviewing!")
	else:
		print("Sorry! Operation cannot be performed. Reviewer does not have authorization to review!")


    def do_REVIEWACCEPT(self,line):
    	tokens = shlex.split(line)

    	#check if the reviewer can review this manuscript 
    	ids = db.REVIEW.find({"REVIEWER_idREVIEWER":self.id},{"ManuscriptID":1, "_id":0})
    	flag = 0
    	for doc in ids:
    		latest_id = doc['ManuscriptID']
    		if latest_id==tokens[0]:
    			flag=1


    	if flag==1:
	    	status = db.MANUSCRIPT.find({"_id": tokens[0]},{"Status":1, "_id":0})
	    	for doc in status:
	    		latest_status = doc['Status']

	    	print (latest_status)
	    	if latest_status=="Under review":
		    	db.REVIEW.update( 
						{"ManuscriptID": tokens[0], "REVIEWER_idREVIEWER" : self.id},
						{ "$set":{"PublicationRecommendation": "Accept", "Clarity": tokens[1], "Methodology": tokens[2], "Contribution": tokens[3], "Appropriateness": tokens[4]} },
						upsert=True )
		    	print ("Updated publication recommendation to Accepted")
		else:
		 	print ("Cannot review this manuscript, not assigned for reviewing!")
	else:
		print("Sorry! Operation cannot be performed. Reviewer does not have authorization to review!")


    def do_accept(self,line):
    	tokens = shlex.split(line)

    	#check if the manuscript is assigned to this editor
    	editorID = db.MANUSCRIPT.find({"_id":tokens[0]},{"EDITOR_idEDITOR":1, "_id":0})

    	for doc in editorID:
    		latest_editorID = doc['EDITOR_idEDITOR']

    	if latest_editorID==self.id:
    		# check if the status of given manuscript is "Under review"
    		status = db.MANUSCRIPT.find({"_id": tokens[0]},{"Status":1, "_id":0})
    		for doc in status:
    			latest_status = doc['Status']
    		if latest_status=="Under review":
    			db.MANUSCRIPT.update({"_id":tokens[0], "EDITOR_idEDITOR":self.id},{"$set":{"Status":"Accepted"}},upsert = True)
    			print("Manuscript ",tokens[0]," status set to \"Accepted\" ")
    		else:
			print("Manuscript does not have the required current status for this action!")

    	else:
    		print("This Editor DOES NOT have the authorization to assign this manuscipt! Try again.") 

    def do_reject(self,line):
    	tokens = shlex.split(line)

    	#check if the manuscript is assigned to this editor
    	editorID = db.MANUSCRIPT.find({"_id":tokens[0]},{"EDITOR_idEDITOR":1, "_id":0})

    	for doc in editorID:
    		latest_editorID = doc['EDITOR_idEDITOR']

    	if latest_editorID==self.id:
    		# check if the status of given manuscript is "Under review"
    		status = db.MANUSCRIPT.find({"_id": tokens[0]},{"Status":1, "_id":0})
    		for doc in status:
    			latest_status = doc['Status']
    		if latest_status=="Under review":
    			db.MANUSCRIPT.update({"_id":tokens[0], "EDITOR_idEDITOR":self.id},{"$set":{"Status":"Rejected"}},upsert = True)
    			print("Manuscript ",tokens[0]," status set to \"Rejected\" ")
    		else:
			print("Manuscript does not have the required current status for this action!")

    	else:
    		print("This Editor DOES NOT have the authorization to assign this manuscipt! Try again.") 






def print_options(table):
	print("\n*****************************")
	print ("What do you wish to to today?")
	print("\n*****************************")

	if table=="AUTHOR":
		print ("\n 1. submit\n 2. STATUS\n 3. RETRACT")
	elif table=="EDITOR":
		print ("\n 1. status\n 2. assign\n 3. reject\n 4. accept\n 5. typeset\n 6. schedule\n 7. publish")
	elif table=="REVIEWER":
		print ("\n 1. REVIEWREJECT\n 2. REVIEWACCEPT")

#main function where the connection happens
if __name__ == "__main__":
	con = MongoClient(SERVER, connect = False, ssl = True)
	con.server_info()
	print("Connection to MegaMongododo Publications DB established.")
	db = con['Team01DB']
	com_intr = command_Line_Interact()
	com_intr.cmdloop()