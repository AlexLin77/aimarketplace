from django.conf import settings

class Metadata(object):
    def __init__(self, request):
        self.session = request.session
        metadata = self.session.get(settings.META_SESSION_ID)

        if not metadata:
            metadata = self.session[settings.META_SESSION_ID] = {}
        
        self.metadata = metadata
    
    def add(self, username, age, gender, region):
        if username not in self.metadata:
            self.metadata[username] = []
            self.metadata[username].append(age)
            self.metadata[username].append(gender)
            self.metadata[username].append(region)
        
        self.save()

    def save(self):
        self.session[settings.META_SESSION_ID] = self.metadata
        self.session.modified = True

        print(self.metadata)
    
    def clear(self):
        del self.session[settings.META_SESSION_ID]
        self.session.modified = True