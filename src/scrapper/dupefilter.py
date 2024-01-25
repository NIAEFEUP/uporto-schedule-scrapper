import uuid

class RequestFingerprinter:
    def fingerprint(self, request):
        # never return an equal value so that every request is scheduled
        return uuid.uuid4().bytes
        
