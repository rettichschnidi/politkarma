#!/bin/sh

set -e                  #Exit script on error
cd "$(dirname "$0")"    #Change to script directory
mkdir -p schemas        #Create subdirectory/ies

fetch()
{
    local URL=${1}
    echo "Fetching ${URL}" >&2
    curl --progress-bar -H 'User-Agent: Mozilla' ${URL}
}

fetchXml()
{
    local URL=${1}
    fetch ${URL} | xmllint --format -
}

#Fetch XSD files
fetchXml 'https://ws.parlament.ch/odata.svc/$metadata' > schemas/global.xml
