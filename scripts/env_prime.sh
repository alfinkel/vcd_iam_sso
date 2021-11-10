#!/usr/bin/bash

# Set IAM_ROOT to the IBM Cloud Identity Access Management root URL.
#   - Change only if targeting a different environment.
export IAM_ROOT="https://iam.cloud.ibm.com"

# Set VCD_ROOT to the virtual Cloud Director root URL.
#   - Replace <vcd> with the vCD short name
export VCD_ROOT="https://<vcd>.vmware-solutions.cloud.ibm.com"

# Set ORG_ADMIN_USR to an admin user @ a vCD organization name.
export ORG_ADMIN_USR="admin@vcd-org-name"

# Set ORG_ADMIN_PWD the ORG_ADMIN_USR's password.
export ORG_ADMIN_PWD="admin-org-pwd"

# Set IAM_CLIENT_ID to a valid IAM client ID for the vCD at VCD_ROOT.
export IAM_CLIENT_ID="iam-client-id"

# Set IAM_CLIENT_SECRET to the IAM_CLIENT_ID's secret.
export IAM_CLIENT_SECRET="iam-client-secret"
