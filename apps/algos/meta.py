from django.conf import settings
import json

class Metadata(object):
    def __init__(self):
        with open('static/users.json', 'r') as jfile:
            metadata = json.load(jfile)
        
        self.metadata = metadata
    
    def add(self, username, age, gender, occupation):
        if username not in self.metadata:
            self.metadata[username] = []
            self.metadata[username].append(age)
            self.metadata[username].append(gender)
            self.metadata[username].append(occupation)
        
        with open('static/users.json', 'w') as jfile:
            json.dump(self.metadata, jfile, indent=4)