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
  fetchXml "http://ws-old.parlament.ch/$n?format=xsd" > xsd-schemas/$n.xsd
  fetchXml "http://ws-old.parlament.ch/$n?format=xml&lang=de" > xml-examples/$n-example.xml
done

#Fetch XML and XSD files from special URL
fetchXml "http://ws-old.parlament.ch/Schedules/2015/ALL?format=xsd" > xsd-schemas/Schedules-2015-ALL.xsd
fetchXml "http://ws-old.parlament.ch/Schedules/2015/ALL?format=xml&lang=de" > xml-examples/Schedules-2015-ALL.xml

#Fetch PDFs
fetch 'http://www.parlament.ch/d/dokumentation/webservices-opendata/Documents/webservices-info-dritte-d.pdf' > 'webservices-info-dritte-d.pdf'
fetch 'http://www.parlament.ch/e/dokumentation/webservices-opendata/Documents/webservices-info-dritte-e.pdf' > 'webservices-info-dritte-e.pdf'
