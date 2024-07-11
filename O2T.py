import requests
import json
import os

okta_domain = os.getenv('OKTA_DOMAIN')
api_token = os.getenv('API_TOKEN')

def fetch_okta_data(endpoint):
    url = f'https://{okta_domain}/api/v1/{endpoint}'
    headers = {
        'Authorization': f'SSWS {api_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code} - {response.text}')
        return None

endpoints = [
    'users',
    'groups',
    'policies?type=MFA_ENROLL',
    'policies?type=OKTA_SIGN_ON',
    'policies?type=PASSWORD',
    'policies?type=IDP_DISCOVERY',
    'authenticators',
    'apps',
    'authorizationServers',
    'idps',
    'roles',
    'logs',
    'inlineHooks'
]

import_commands = []

for endpoint in endpoints:
    print(f'Fetching data from /api/v1/{endpoint}')
    data = fetch_okta_data(endpoint)
    if data:
        filename = f"{endpoint.replace('?', '_').replace('=', '_')}.json"
        with open(filename, 'w') as outfile:
            json.dump(data, outfile, indent=4)
        print(f'Data has been written to {filename}')

        tf_filename = f"{endpoint.replace('?', '_').replace('=', '_')}.tf"
        with open(tf_filename, 'w') as tf_file:
            if endpoint == 'users':
                for user in data:
                    resource_name = f'okta_user.{user["id"]}'
                    tf_file.write(f'resource "okta_user" "{user["id"]}" {{\n')
                    tf_file.write(f'  login = "{user["profile"]["login"]}"\n')
                    tf_file.write(f'  email = "{user["profile"]["email"]}"\n')
                    tf_file.write(f'  first_name = "{user["profile"]["firstName"]}"\n')
                    tf_file.write(f'  last_name = "{user["profile"]["lastName"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {user["id"]}')
            elif endpoint == 'groups':
                for group in data:
                    resource_name = f'okta_group.{group["id"]}'
                    tf_file.write(f'resource "okta_group" "{group["id"]}" {{\n')
                    tf_file.write(f'  name = "{group["profile"]["name"]}"\n')
                    tf_file.write(f'  description = "{group["profile"]["description"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {group["id"]}')
            elif endpoint.startswith('policies'):
                for policy in data:
                    resource_name = f'okta_policy.{policy["id"]}'
                    tf_file.write(f'resource "okta_policy" "{policy["id"]}" {{\n')
                    tf_file.write(f'  name = "{policy["name"]}"\n')
                    tf_file.write(f'  type = "{policy["type"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {policy["id"]}')
            elif endpoint == 'authenticators':
                for authenticator in data:
                    resource_name = f'okta_authenticator.{authenticator["id"]}'
                    tf_file.write(f'resource "okta_authenticator" "{authenticator["id"]}" {{\n')
                    tf_file.write(f'  name = "{authenticator["name"]}"\n')
                    tf_file.write(f'  type = "{authenticator["type"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {authenticator["id"]}')
            elif endpoint == 'apps':
                for app in data:
                    resource_name = f'okta_app.{app["id"]}'
                    tf_file.write(f'resource "okta_app" "{app["id"]}" {{\n')
                    tf_file.write(f'  label = "{app["label"]}"\n')
                    tf_file.write(f'  sign_on_mode = "{app["signOnMode"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {app["id"]}')
            elif endpoint == 'authorizationServers':
                for server in data:
                    resource_name = f'okta_authorization_server.{server["id"]}'
                    tf_file.write(f'resource "okta_authorization_server" "{server["id"]}" {{\n')
                    tf_file.write(f'  name = "{server["name"]}"\n')
                    tf_file.write(f'  description = "{server["description"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {server["id"]}')
            elif endpoint == 'idps':
                for idp in data:
                    resource_name = f'okta_idp.{idp["id"]}'
                    tf_file.write(f'resource "okta_idp" "{idp["id"]}" {{\n')
                    tf_file.write(f'  name = "{idp["name"]}"\n')
                    tf_file.write(f'  type = "{idp["type"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {idp["id"]}')
            elif endpoint == 'roles':
                for role in data:
                    resource_name = f'okta_role.{role["id"]}'
                    tf_file.write(f'resource "okta_role" "{role["id"]}" {{\n')
                    tf_file.write(f'  label = "{role["label"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {role["id"]}')
            elif endpoint == 'inlineHooks':
                for hook in data:
                    resource_name = f'okta_inline_hook.{hook["id"]}'
                    tf_file.write(f'resource "okta_inline_hook" "{hook["id"]}" {{\n')
                    tf_file.write(f'  name = "{hook["name"]}"\n')
                    tf_file.write(f'  type = "{hook["type"]}"\n')
                    tf_file.write('}\n\n')
                    import_commands.append(f'terraform import {resource_name} {hook["id"]}')
        print(f'Terraform configuration has been written to {tf_filename}')

with open('import_commands.sh', 'w') as import_file:
    import_file.write('#!/bin/sh\n\n')
    for command in import_commands:
        import_file.write(f'{command}\n')

print('Import commands have been written to import_commands.sh')
