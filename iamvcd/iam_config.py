# -*- mode:python; coding:utf-8 -*-

import os
import requests
from base64 import urlsafe_b64decode
from xml.dom.minidom import parseString, Document

from Crypto.Util.number import bytes_to_long
from Crypto.PublicKey import RSA


IAM_IDENTITY = f'{os.getenv("IAM_ROOT")}/identity'
VCD_API = f'{os.getenv("VCD_ROOT")}/api'


def get_iam_openid_config():
    resp = requests.get(f'{IAM_IDENTITY}/.well-known/openid-configuration')
    resp.raise_for_status()
    config = resp.json()
    scopes = ['openid', 'email', 'profile']
    if not set(scopes).issubset(set(config['scopes_supported'])):
        raise ValueError(f'Scopes {scopes} not supported.')
    fields = [
        'issuer',
        'authorization_endpoint',
        'token_endpoint',
        'userinfo_endpoint'
    ]
    return {**{field: config[field] for field in fields}, **{'scopes': scopes}}


def get_iam_oauth_keys():
    resp = requests.get(f'{IAM_IDENTITY}/keys')
    resp.raise_for_status()
    return resp.json()['keys']


def jwk_to_pem(*components):
    rsa_components = (bytes_to_long(urlsafe_b64decode(c)) for c in components)
    return RSA.construct(rsa_components).export_key().decode()


def get_latest_vcd_api_version():
    resp = requests.get(f'{VCD_API}/versions')
    resp.raise_for_status()
    versions = [
        v.getElementsByTagName('Version')[0].firstChild.data
        for v in parseString(resp.text).getElementsByTagName('VersionInfo')
        if v.getAttribute('deprecated') == 'false'
    ]
    return versions[-1]


def get_vcd_api_session_info(version=None):
    if version is None:
        version = get_latest_vcd_api_version()
    content_type = (
        f'application/vnd.vmware.vcloud.session+xml;version={version}'
    )
    headers = {
        'Accept': f'application/*+xml;version={version}',
        'Content-Type': content_type
    }
    auth = (os.getenv('ORG_ADMIN_USR'), os.getenv('ORG_ADMIN_PWD'))
    resp = requests.post(f'{VCD_API}/sessions', auth=auth, headers=headers)
    resp.raise_for_status()
    loc_id = parseString(resp.text).documentElement.getAttribute('locationId')
    return resp.headers['X-VMWARE-VCLOUD-ACCESS-TOKEN'], loc_id.split('@')[0]


def get_org_admin_role_link(version=None, token=None, org_id=None):
    if version is None:
        version = get_latest_vcd_api_version()
    if token is None or org_id is None:
        token, org_id = get_vcd_api_session_info(version)
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': f'application/*+json;version={version}'
    }
    params = {
        'format': 'records', 'filter': 'name==Organization Administrator'
    }
    resp = requests.get(
        f'{VCD_API}/admin/org/{org_id}/roles/query',
        headers=headers,
        params=params
    )
    resp.raise_for_status()
    return resp.json()['record'][0]['href']


def integrate_vcd_with_iam(version=None, token=None, org_id=None):
    if version is None:
        version = get_latest_vcd_api_version()
    if token is None or org_id is None:
        token, org_id = get_vcd_api_session_info(version)
    content_type = 'application/vnd.vmware.admin.organizationOAuthSettings+xml'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': f'application/*+xml;version={version}',
        'Content-Type': content_type
    }
    iam_config = get_iam_openid_config()
    doc = Document()
    org_oauth_settings = doc.createElement('OrgOAuthSettings')
    org_oauth_settings.setAttribute(
        'xmlns', 'http://www.vmware.com/vcloud/v1.5'
    )
    org_oauth_settings.setAttribute('type', content_type)
    oauth_settings = {
        doc.createElement('IssuerId'): lambda p, d: add_child(
            p, d, iam_config['issuer']
        ),
        doc.createElement('OAuthKeyConfigurations'): handle_oauth_configs,
        doc.createElement('Enabled'): lambda p, d: add_child(p, d, 'true'),
        doc.createElement('ClientId'): lambda p, d: add_child(
            p, d, os.getenv('IAM_CLIENT_ID')
        ),
        doc.createElement('ClientSecret'): lambda p, d: add_child(
            p, d, os.getenv('IAM_CLIENT_SECRET')
        ),
        doc.createElement('UserAuthorizationEndpoint'): lambda p, d: add_child(
            p, d, iam_config['authorization_endpoint']
        ),
        doc.createElement('AccessTokenEndpoint'): lambda p, d: add_child(
            p, d, iam_config['token_endpoint']
        ),
        doc.createElement('UserInfoEndpoint'): lambda p, d: add_child(
            p, d, iam_config['userinfo_endpoint']
        ),
        doc.createElement('Scope'): lambda p, d: add_child(
            p, d, ' '.join(iam_config['scopes'])
        ),
        doc.createElement('OIDCAttributeMapping'): handle_oidc_mappings,
        doc.createElement('MaxClockSkew'): lambda p, d: add_child(p, d, '600')
    }
    for element, handle_content in oauth_settings.items():
        handle_content(element, doc)
        org_oauth_settings.appendChild(element)
    doc.appendChild(org_oauth_settings)
    resp = requests.put(
        f'{VCD_API}/admin/org/{org_id}/settings/oauth',
        headers=headers,
        data=doc.toxml()
    )
    resp.raise_for_status()


def add_child(parent, doc, node_content):
    parent.appendChild(doc.createTextNode(node_content))


def handle_oauth_configs(parent, doc):
    for key in get_iam_oauth_keys():
        oauth_key_config = doc.createElement('OAuthKeyConfiguration')
        key_settings = {
            doc.createElement('KeyId'): key['kid'],
            doc.createElement('Algorithm'): key['kty'],
            doc.createElement('Key'): jwk_to_pem(f'{key["n"]}==', key['e'])
        }
        for element, node_content in key_settings.items():
            add_child(element, doc, node_content)
            oauth_key_config.appendChild(element)
        parent.appendChild(oauth_key_config)


def handle_oidc_mappings(parent, doc):
    mappings = {
        doc.createElement('SubjectAttributeName'): 'email',
        doc.createElement('EmailAttributeName'): 'email',
        doc.createElement('FirstNameAttributeName'): 'given_name',
        doc.createElement('LastNameAttributeName'): 'family_name',
        doc.createElement('GroupsAttributeName'): 'groups',
        doc.createElement('RolesAttributeName'): 'roles'
    }
    for element, node_content in mappings.items():
        add_child(element, doc, node_content)
        parent.appendChild(element)


def import_iam_user(username, version=None, token=None, org_id=None):
    if version is None:
        version = get_latest_vcd_api_version()
    if token is None or org_id is None:
        token, org_id = get_vcd_api_session_info(version)
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': f'application/*+json;version={version}',
        'Content-Type': 'application/vnd.vmware.admin.user+xml'
    }
    doc = Document()
    user = doc.createElement('User')
    user.setAttribute('xmlns', 'http://www.vmware.com/vcloud/v1.5')
    user.setAttribute('name', username)
    user_settings = {
        doc.createElement('IsEnabled'): 'true',
        doc.createElement('IsExternal'): 'true',
        doc.createElement('ProviderType'): 'OAUTH'
    }
    for element, node_content in user_settings.items():
        add_child(element, doc, node_content)
        user.appendChild(element)
    role = doc.createElement('Role')
    role.setAttribute('href', get_org_admin_role_link(version, token, org_id))
    user.appendChild(role)
    doc.appendChild(user)
    resp = requests.post(
        f'{VCD_API}/admin/org/{org_id}/users',
        headers=headers,
        data=doc.toxml()
    )
    resp.raise_for_status()
