#!/bin/sh

set -e                              #Exit script on error
cd "$(dirname "$0")"                #Change to script directory
mkdir -p xml-examples xsd-schemas   #Create subdirectories

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

#Fetch XML and XSD documents
for n in Councils Councillors Schedules Affairs AffairSummaries Committees LegislativePeriods Departments Cantons Factions Sessions Parties Votes; do
  fetchXml "http://ws.parlament.ch/$n?format=xsd" > xsd-schemas/$n.xsd
  fetchXml "http://ws.parlament.ch/$n?format=xml&lang=en" > xml-examples/$n-example.xml
done

#Fetch PDFs
fetch 'http://www.parlament.ch/d/dokumentation/webservices-opendata/Documents/webservices-info-dritte-d.pdf' > 'webservices-info-dritte-d.pdf'
fetch 'http://www.parlament.ch/e/dokumentation/webservices-opendata/Documents/webservices-info-dritte-e.pdf' > 'webservices-info-dritte-e.pdf'
