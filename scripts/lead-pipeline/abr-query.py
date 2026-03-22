"""
ABR API Query — New WA Business Registrations
Queries the Australian Business Register for businesses registered yesterday in WA.
Called by n8n via Execute Command node.

Usage:
    python abr-query.py                    # Yesterday's registrations
    python abr-query.py --date 2026-03-19  # Specific date
    python abr-query.py --days 7           # Last 7 days

Output: JSON array to stdout (n8n reads this)
"""

import sys
import json
import argparse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError
import os
from dotenv import load_dotenv

load_dotenv()

ABR_GUID = os.getenv('ABR_GUID')
if not ABR_GUID:
    print(json.dumps({"error": "ABR_GUID not set in .env"}), file=sys.stderr)
    sys.exit(1)

ABR_ENDPOINT = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx"

# Perth metro postcodes (6000-6999 covers all of Perth metro + surrounds)
PERTH_POSTCODES = set(str(p) for p in range(6000, 7000))

# Residential address classification (credit: Aaron's girlfriend)
# Businesses at home addresses are more likely to be owner-operated and need help.
CBD_POSTCODES = {'6000', '6001', '6003', '6004', '6005'}
COMMERCIAL_INDUSTRIAL_POSTCODES = {
    '6017', '6021', '6053', '6054', '6055', '6065', '6090',
    '6100', '6104', '6105', '6106', '6107', '6109', '6112',
    '6154', '6155', '6163', '6164', '6165', '6166', '6168',
}


def classify_postcode(postcode):
    """Classify a Perth postcode as residential, commercial, or cbd."""
    if not postcode:
        return 'unknown'
    pc = str(postcode).strip()
    if pc in CBD_POSTCODES:
        return 'cbd'
    if pc in COMMERCIAL_INDUSTRIAL_POSTCODES:
        return 'commercial'
    return 'residential'


def query_abr_by_name(name_search, state='WA'):
    """Search ABR by business name to find WA businesses."""
    soap_body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"
                 xmlns:abr="http://abr.business.gov.au/ABRXMLSearch/">
  <soap12:Body>
    <abr:ABRSearchByNameAdvancedSimpleProtocol2017>
      <abr:name>{name_search}</abr:name>
      <abr:postcode></abr:postcode>
      <abr:legalName>Y</abr:legalName>
      <abr:tradingName>Y</abr:tradingName>
      <abr:businessName>Y</abr:businessName>
      <abr:activeABNsOnly>Y</abr:activeABNsOnly>
      <abr:NSW>N</abr:NSW>
      <abr:SA>N</abr:SA>
      <abr:ACT>N</abr:ACT>
      <abr:VIC>N</abr:VIC>
      <abr:WA>Y</abr:WA>
      <abr:NT>N</abr:NT>
      <abr:QLD>N</abr:QLD>
      <abr:TAS>N</abr:TAS>
      <abr:authenticationGuid>{ABR_GUID}</abr:authenticationGuid>
      <abr:searchWidth>typical</abr:searchWidth>
      <abr:minimumScore>80</abr:minimumScore>
      <abr:maxSearchResults>200</abr:maxSearchResults>
    </abr:ABRSearchByNameAdvancedSimpleProtocol2017>
  </soap12:Body>
</soap12:Envelope>"""

    headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8',
    }

    req = Request(ABR_ENDPOINT, data=soap_body.encode('utf-8'), headers=headers, method='POST')

    try:
        with urlopen(req, timeout=30) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(json.dumps({"error": f"ABR API request failed: {str(e)}"}), file=sys.stderr)
        return None


def query_abr_by_abn(abn):
    """Look up a specific ABN for full details."""
    url = f"https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/SearchByABNv202001?searchString={abn}&includeHistoricalDetails=N&authenticationGuid={ABR_GUID}"

    try:
        req = Request(url)
        with urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except URLError as e:
        print(json.dumps({"error": f"ABR lookup failed for {abn}: {str(e)}"}), file=sys.stderr)
        return None


def search_new_registrations(target_date, trade_categories=None):
    """
    Search for newly registered WA businesses.
    ABR doesn't have a direct 'registrations on date X' endpoint,
    so we search by common trade category names and filter by registration date.
    """
    if trade_categories is None:
        trade_categories = [
            "plumber", "plumbing",
            "electrician", "electrical",
            "builder", "building",
            "landscap", "landscape",
            "clean", "cleaning",
            "paint", "painter",
            "roof", "roofing",
            "concret", "concreting",
            "fenc", "fencing",
            "carpent", "carpentry",
            "pest control",
            "air conditioning", "aircon",
            "solar",
            "pool",
            "bore", "drilling",
            "excavat", "demolition",
            "handyman",
            "tiling", "tiler",
            "garage door",
            "glass", "glazier",
        ]

    all_results = []
    seen_abns = set()

    for category in trade_categories:
        xml_response = query_abr_by_name(category, state='WA')
        if not xml_response:
            continue

        leads = parse_abr_response(xml_response, target_date)
        for lead in leads:
            if lead['abn'] not in seen_abns:
                seen_abns.add(lead['abn'])
                all_results.append(lead)

    return all_results


def parse_abr_response(xml_text, target_date=None):
    """Parse ABR XML response into lead objects."""
    leads = []

    # Remove namespaces for easier parsing
    xml_text = xml_text.replace('xmlns=', 'xmlnsignore=')

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(json.dumps({"error": f"XML parse error: {str(e)}"}), file=sys.stderr)
        return leads

    # Find all search result records
    for record in root.iter('searchResultsRecord'):
        try:
            abn_elem = record.find('.//ABN/identifierValue')
            if abn_elem is None:
                continue
            abn = abn_elem.text

            # Get business name (try trading name first, then main name)
            name = ''
            for name_tag in ['businessName', 'mainTradingName', 'mainName', 'legalName']:
                name_elem = record.find(f'.//{name_tag}/organisationName')
                if name_elem is not None and name_elem.text:
                    name = name_elem.text
                    break
            if not name:
                name_elem = record.find('.//mainName/familyName')
                if name_elem is not None:
                    given = record.find('.//mainName/givenName')
                    name = f"{given.text} {name_elem.text}" if given is not None else name_elem.text

            # Get state and postcode
            state_elem = record.find('.//mainBusinessPhysicalAddress/stateCode')
            postcode_elem = record.find('.//mainBusinessPhysicalAddress/postcode')

            state = state_elem.text if state_elem is not None else ''
            postcode = postcode_elem.text if postcode_elem is not None else ''

            # Filter: WA only, Perth postcodes
            if state != 'WA':
                continue
            if postcode and postcode not in PERTH_POSTCODES:
                continue

            # Get registration date
            reg_date_elem = record.find('.//ABN/replacedFrom')
            if reg_date_elem is None:
                reg_date_elem = record.find('.//ASICNumber/replacedFrom')

            reg_date = None
            if reg_date_elem is not None and reg_date_elem.text:
                try:
                    reg_date = datetime.strptime(reg_date_elem.text[:10], '%Y-%m-%d').date()
                except ValueError:
                    pass

            # If filtering by date, skip old registrations
            if target_date and reg_date:
                if reg_date < target_date - timedelta(days=7):
                    continue

            # Get entity type
            entity_elem = record.find('.//entityType/entityDescription')
            entity_type = entity_elem.text if entity_elem is not None else ''

            lead = {
                'business_name': name.strip(),
                'abn': abn.strip(),
                'postcode': postcode,
                'state': 'WA',
                'entity_type': entity_type,
                'registration_date': str(reg_date) if reg_date else None,
                'source': 'abr',
                'pipeline': 'no_website',
                'category': '',  # ABR doesn't classify by trade — enrichment needed
                'address_type': classify_postcode(postcode),
            }

            leads.append(lead)

        except Exception as e:
            print(json.dumps({"warning": f"Error parsing record: {str(e)}"}), file=sys.stderr)
            continue

    return leads


def main():
    parser = argparse.ArgumentParser(description='Query ABR for new WA business registrations')
    parser.add_argument('--date', type=str, help='Target date (YYYY-MM-DD). Default: yesterday')
    parser.add_argument('--days', type=int, default=1, help='Number of days to look back. Default: 1')
    args = parser.parse_args()

    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        target_date = (datetime.now() - timedelta(days=args.days)).date()

    results = search_new_registrations(target_date)

    # Output JSON to stdout for n8n
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
