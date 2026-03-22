// Perth Postcode Classifier — Residential Address Detection
// Insight credit: Aaron's girlfriend — businesses registered at home addresses
// are more likely to be owner-operated and need marketing help.
//
// Usage: copy classifyPostcode() into n8n Code nodes (both Pipeline A and B).
// Called during enrichment before scoring. Result stored in leads.address_type.
//
// Classification:
//   'residential'  — suburban Perth (default). +2 score boost in lead scoring.
//   'commercial'   — known industrial/commercial zones. +0 (neutral).
//   'cbd'          — Perth city centre. +0 (neutral).
//   'unknown'      — no postcode available.

const CBD_POSTCODES = new Set([
  '6000', '6001', '6003', '6004', '6005'
]);

const COMMERCIAL_INDUSTRIAL_POSTCODES = new Set([
  // North-West: Osborne Park, Balcatta, Wangara, Malaga
  '6017', '6021', '6065', '6090',
  // North-East: Bayswater, Bassendean, Hazelmere
  '6053', '6054', '6055',
  // South-East: Vic Park, Belmont, Kewdale, Welshpool, Cannington, Maddington, Forrestdale, Canning Vale
  '6100', '6104', '6105', '6106', '6107', '6109', '6112', '6155',
  // South-West: Myaree, Bibra Lake/O'Connor, Jandakot, Naval Base, Henderson, Rockingham
  '6154', '6163', '6164', '6165', '6166', '6168'
]);

function classifyPostcode(postcode) {
  if (!postcode) return 'unknown';
  const pc = String(postcode).trim();
  if (CBD_POSTCODES.has(pc)) return 'cbd';
  if (COMMERCIAL_INDUSTRIAL_POSTCODES.has(pc)) return 'commercial';
  return 'residential';
}

// For use in n8n Code nodes — just copy the function above.
// For Node.js scripts:
if (typeof module !== 'undefined') {
  module.exports = { classifyPostcode, CBD_POSTCODES, COMMERCIAL_INDUSTRIAL_POSTCODES };
}
