import json
 
dictionary = {}

x = int(input("Enter number: "))
for i in range(x):
    key = input("Enter key: ")
    value = input("Enter value: ")

    dictionary[key] = value

 
# Serializing json
json_object = json.dumps(dictionary, indent=4)
 
# Writing to sample.json
with open("file.json", "w") as outfile:
    outfile.write(json_object)