import pandas as pd
import json
import re

# Expanded Dictionary: 1875 Railway Locations & Coordinates
# Includes historical counties for spatial context
geo_dict = {
    'London': [51.5074, -0.1278, 'Middlesex'], 'Battersea': [51.4707, -0.1547, 'Surrey'],
    'Manchester': [53.4808, -2.2426, 'Lancashire'], 'Liverpool': [53.4084, -2.9916, 'Lancashire'],
    'Birmingham': [52.4862, -1.8904, 'Warwickshire'], 'Leeds': [53.8008, -1.5491, 'Yorkshire'],
    'Sheffield': [53.3811, -1.4701, 'Yorkshire'], 'Bristol': [51.4545, -2.5879, 'Gloucestershire'],
    'Newcastle': [54.9783, -1.6178, 'Northumberland'], 'Derby': [52.9225, -1.4761, 'Derbyshire'],
    'Nottingham': [52.9548, -1.1581, 'Nottinghamshire'], 'Leicester': [52.6333, -1.1333, 'Leicestershire'],
    'Doncaster': [53.5228, -1.1285, 'Yorkshire'], 'York': [53.9591, -1.0815, 'Yorkshire'],
    'Crewe': [53.0990, -2.4410, 'Cheshire'], 'Peterborough': [52.5695, -0.2405, 'Northamptonshire'],
    'Reading': [51.4543, -0.9781, 'Berkshire'], 'Swindon': [51.5558, -1.7797, 'Wiltshire'],
    'Brighton': [50.8225, -0.1372, 'Sussex'], 'Plymouth': [50.3755, -4.1427, 'Devon'],
    'Cardiff': [51.4816, -3.1791, 'Glamorgan'], 'Newport': [51.5883, -2.9975, 'Monmouthshire'],
    'Swansea': [51.6214, -3.9436, 'Glamorgan'], 'Glasgow': [55.8642, -4.2518, 'Lanarkshire'],
    'Edinburgh': [55.9533, -3.1883, 'Midlothian'], 'Aberdeen': [57.1497, -2.0943, 'Aberdeenshire'],
    'Huddersfield': [53.6450, -1.7850, 'Yorkshire'], 'Barnsley': [53.5526, -1.4797, 'Yorkshire'],
    'Dudley': [52.5123, -2.0811, 'Worcestershire'], 'Guildford': [51.2362, -0.5704, 'Surrey'],
    'Blackburn': [53.7480, -2.4820, 'Lancashire'], 'Burnley': [53.7893, -2.2482, 'Lancashire'],
    'Preston': [53.7609, -2.7033, 'Lancashire'], 'Stockport': [53.4106, -2.1575, 'Cheshire'],
    'Wolverhampton': [52.5870, -2.1287, 'Staffordshire'], 'Rugby': [52.3709, -1.2607, 'Warwickshire'],
    'Bletchley': [51.9937, -0.7323, 'Buckinghamshire'], 'Bedford': [52.1360, -0.4667, 'Bedfordshire'],
    'Kettering': [52.3961, -0.7289, 'Northamptonshire'], 'Gloucester': [51.8642, -2.2444, 'Gloucestershire'],
    'Oxford': [51.7520, -1.2577, 'Oxfordshire'], 'Cambridge': [52.2053, 0.1218, 'Cambridgeshire'],
    'Exeter': [50.7184, -3.5339, 'Devon'], 'Salisbury': [51.0688, -1.7945, 'Wiltshire'],
    'Portsmouth': [50.8198, -1.0880, 'Hampshire'], 'Southampton': [50.9097, -1.4044, 'Hampshire'],
    'Chester': [53.1905, -2.8915, 'Cheshire'], 'Shrewsbury': [52.7073, -2.7553, 'Shropshire'],
    'Stafford': [52.8066, -2.1171, 'Staffordshire'], 'Carlisle': [54.8925, -2.9329, 'Cumberland'],
    'Lincoln': [53.2268, -0.5378, 'Lincolnshire'], 'Grimsby': [53.5651, -0.0813, 'Lincolnshire'],
    'Ambergate': [53.0645, -1.4825, 'Derbyshire'], 'Whitworth': [53.6450, -2.1790, 'Lancashire'],
    'Crystal Palace': [51.4215, -0.0706, 'Kent'], 'Battersea': [51.4707, -0.1547, 'Surrey'],
    'Camden': [51.5455, -0.1411, 'Middlesex'], 'Nine Elms': [51.4815, -0.1285, 'Surrey'],
    'King\'s Cross': [51.5322, -0.1232, 'Middlesex'], 'St Pancras': [51.5300, -0.1250, 'Middlesex'],
    'Stratford': [51.5417, 0.0036, 'Essex'], 'Willesden': [51.5486, -0.2435, 'Middlesex'],
    'Burton': [52.8055, -1.6360, 'Staffordshire'], 'Middleton': [53.5544, -2.1887, 'Lancashire'],
    'Salford': [53.4875, -2.2901, 'Lancashire'], 'Bradford': [53.7938, -1.7515, 'Yorkshire'],
    'Normanton': [53.6980, -1.4210, 'Yorkshire'], 'Chesterfield': [53.2350, -1.4216, 'Derbyshire'],
    'Accrington': [53.7534, -2.3644, 'Lancashire'], 'Bury': [53.5933, -2.2967, 'Lancashire'],
    'Bolton': [53.5810, -2.4282, 'Lancashire'], 'Wigan': [53.5448, -2.6318, 'Lancashire'],
    'Rochdale': [53.6144, -2.1600, 'Lancashire'], 'Warrington': [53.3901, -2.5970, 'Lancashire'],
    'Widnes': [53.3630, -2.7280, 'Lancashire'], 'Runcorn': [53.3410, -2.7300, 'Cheshire'],
    'Mold': [53.1670, -3.1430, 'Flintshire'], 'Tredegar': [51.7719, -3.2435, 'Monmouthshire'],
    'Merthyr': [51.7470, -3.3780, 'Glamorgan'], 'Highbridge': [51.2197, -2.9734, 'Somerset'],
    'Radstock': [51.2910, -2.4470, 'Somerset'], 'Bath': [51.3758, -2.3599, 'Somerset']
}

def clean_location(name):
    if pd.isna(name): return None
    name = str(name).strip()
    # Remove "Branch", "Junction", "Lodge", and OCR noise
    name = re.sub(r'(?i)\b(Branch|No\.?|Lodge|Loyal Hope|Function|Junction|RECEIVING|UNSPECIFIED|Annual Balance Sheet.*)\b', '', name)
    name = re.sub(r'[0-9]', '', name).strip(', .()-')
    
    # Manual OCR corrections for common errors in your file
    corrections = {
        'Cusstal Palace': 'Crystal Palace', 'Batteriza': 'Battersea', 'Brightom': 'Brighton',
        'rmanton': 'Normanton', 'Dudy': 'Dudley', 'Cheter': 'Chester', 'Hy HawBridge': 'Highbridge',
        'Conden': 'Camden', 'Batter sea': 'Battersea', 'Camb ': 'Cambridge'
    }
    for typo, fix in corrections.items():
        if typo in name: name = fix
    return name

df = pd.read_csv('extracted_railway_results.csv')
df['cleaned_loc'] = df['branch'].apply(clean_location)

markers = []
unmatched = []

for _, row in df.iterrows():
    loc = row['cleaned_loc']
    matched = False
    # Check for direct or partial match (e.g., "Derby No. 1" matches "Derby")
    for key in geo_dict:
        if loc and (key.lower() in loc.lower() or loc.lower() in key.lower()):
            data = geo_dict[key]
            markers.append({
                'loc': key, 'lat': data[0], 'lon': data[1], 'county': data[2],
                'members': str(row['member_count']), 'file': row['filename']
            })
            matched = True
            break
    if not matched and loc:
        unmatched.append(loc)

# Generate HTML Map
leaflet_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>1875 Railway Union Map</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>#map {{ height: 100vh; width: 100%; }}</style>
</head>
<body>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([53.5, -2.0], 6);
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png').addTo(map);
        var markers = {json.dumps(markers)};
        markers.forEach(function(m) {{
            L.marker([m.lat, m.lon]).bindPopup("<b>" + m.loc + "</b><br>1875 County: " + m.county + "<br>Members: " + m.members).addTo(map);
        }});
    </script>
</body>
</html>
"""

with open('railway_map_1875.html', 'w', encoding='utf-8') as f:
    f.write(leaflet_html)

print(f"Success! Map generated with {len(markers)} pins.")
print(f"Top unmatched locations to add: {set(unmatched[:10])}")
