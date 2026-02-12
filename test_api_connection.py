from data_extraction.api_client import SportRadarClient
import time

def test_api():
    try:
        client = SportRadarClient()
        
        print("Testing Competitions API...")
        comp_data = client.get_competitions()
        print(f"✓ Competitions API working! Found {len(comp_data.get('competitions', []))} competitions")
        
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        print("Testing Complexes API...")
        complex_data = client.get_complexes()
        print(f"✓ Complexes API working! Found {len(complex_data.get('complexes', []))} complexes")
        
        print("\nWaiting 2 seconds...")
        time.sleep(2)
        
        print("Testing Rankings API...")
        rankings_data = client.get_rankings()  # Changed from get_doubles_rankings
        print(f"✓ Rankings API working! Found {len(rankings_data.get('rankings', []))} rankings")
        
        print("\n✓✓✓ All API endpoints working! ✓✓✓")
        
    except Exception as e:
        print(f"✗ API test failed: {e}")

if __name__ == "__main__":
    test_api()