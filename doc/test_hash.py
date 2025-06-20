from documents.models import Document
from utils.hashid import encode_id
doc = Document.objects.all().order_by('id')[4] 

hashid = encode_id(doc.id)

print("Document ID:", doc.id)
print("HashID:", hashid)