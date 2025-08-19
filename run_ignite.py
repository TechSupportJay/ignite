import os, json

path = "/mnt/3C1C05611C051792/Programming/Python/Ignite/ContentFolder/"
if os.path.exists("C:/Windows"): path = "D:\Programming\Python\Ignite\ContentFolder"

data_file = json.load(open("Data/Profile1/options.json"))
data_file["Customisation"]["content_folder"] = path

save_file = open("Data/Profile1/options.json", "w")
save_file.write(json.dumps(data_file))
save_file.close()

print("Starting...")

os.system("python ./master.py")