from data_extraction.api_client import SportRadarClient
import json

client = SportRadarClient()

print("="*60)
print("Testing Competitions API")
print("="*60)
comp_data = client.get_competitions()
if 'competitions' in comp_data and len(comp_data['competitions']) > 0:
    sample = comp_data['competitions'][0]
    print(f"Sample competition: {json.dumps(sample, indent=2)}")
    
    # Check parent_id pattern
    with_parent = [c for c in comp_data['competitions'] if c.get('parent_id')]
    print(f"\nCompetitions with parent_id: {len(with_parent)}")
    if with_parent:
        print(f"Sample parent_id: {with_parent[0].get('parent_id')}")
        print(f"Sample competition_id: {with_parent[0].get('id')}")

print("\n" + "="*60)
print("Testing Rankings API")
print("="*60)

# Test different endpoint variations
endpoints_to_try = [
    "rankings.json",
    "doubles/rankings.json",
    "competitor_rankings.json",
    "double_competitor_rankings.json"
]

for endpoint in endpoints_to_try:
    try:
        print(f"\nTrying: {endpoint}")
        data = client._make_request(endpoint)
        if data and 'rankings' in data:
            print(f"✓ SUCCESS! Found {len(data['rankings'])} rankings")
            print(f"Sample: {json.dumps(data['rankings'][0], indent=2)[:500]}")
            break
    except Exception as e:
        print(f"✗ Failed: {str(e)[:100]}")