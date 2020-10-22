import os

path = os.path.abspath(os.path.dirname(__file__)).replace("\\","/")

file_path = path + "/FileToDelete.txt"


f = open(file_path)

line = f.readline()

while line:
  delete_path = path + line[19:].replace('\n','')

  if os.path.exists(delete_path):
    os.remove(delete_path)
  else:
    print(delete_path + "The file does not exist \n")
  
  line = f.readline()
  
f.close()

