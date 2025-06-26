import json

with open("src/example.json", 'r') as f:
    content = json.load(f)

page = ""

for section in content:
    for header, body in section.items():
        h_tag = body["tag"]
        page += f"<{h_tag}>" + header + f"<{h_tag}>" + body["html"] 
        
with open("final.html", 'w') as f:
    f.write(page)