import json
with open('python-sbom.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
licenses = set()
for component in data['components']:
    for license_info in component.get('licenses', []):
        license = license_info.get('license')
        if license and 'id' in license:
            licenses.add(license['id'])

print(licenses)