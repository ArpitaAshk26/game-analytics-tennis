import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from database.db_connection import DatabaseConnection

class DatabaseHelper:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def execute_query(self, query):
        """Execute a SQL query and return results as DataFrame"""
        conn = self.db.get_pyodbc_connection()
        try:
            df = pd.read_sql(query, conn)
            return df
        finally:
            conn.close()
    
    # ============= COMPETITION QUERIES =============
    
    def get_all_competitions_with_category(self):
        query = """
        SELECT 
            c.competition_id,
            c.competition_name,
            cat.category_name,
            c.type,
            c.gender,
            c.parent_id
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        ORDER BY cat.category_name, c.competition_name
        """
        return self.execute_query(query)
    
    def get_competitions_count_by_category(self):
        query = """
        SELECT 
            cat.category_name,
            COUNT(*) as competition_count
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY competition_count DESC
        """
        return self.execute_query(query)
    
    def get_doubles_competitions(self):
        query = """
        SELECT 
            c.competition_name,
            cat.category_name,
            c.gender
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        WHERE c.type = 'doubles'
        ORDER BY cat.category_name, c.competition_name
        """
        return self.execute_query(query)
    
    def get_competitions_by_category(self, category_name):
        query = f"""
        SELECT 
            c.competition_name,
            c.type,
            c.gender
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        WHERE cat.category_name = '{category_name}'
        ORDER BY c.competition_name
        """
        return self.execute_query(query)
    
    def get_parent_child_competitions(self):
        query = """
        SELECT 
            p.competition_name as parent_competition,
            c.competition_name as child_competition,
            c.type,
            c.gender
        FROM Competitions c
        INNER JOIN Competitions p ON c.parent_id = p.competition_id
        ORDER BY p.competition_name, c.competition_name
        """
        return self.execute_query(query)
    
    def get_competition_type_distribution(self):
        query = """
        SELECT 
            cat.category_name,
            c.type,
            COUNT(*) as count
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        GROUP BY cat.category_name, c.type
        ORDER BY cat.category_name, c.type
        """
        return self.execute_query(query)
    
    def get_top_level_competitions(self):
        query = """
        SELECT 
            c.competition_name,
            cat.category_name,
            c.type,
            c.gender
        FROM Competitions c
        INNER JOIN Categories cat ON c.category_id = cat.category_id
        WHERE c.parent_id IS NULL
        ORDER BY cat.category_name, c.competition_name
        """
        return self.execute_query(query)
    
    # ============= VENUE QUERIES =============
    
    def get_all_venues_with_complex(self):
        query = """
        SELECT 
            v.venue_name,
            c.complex_name,
            v.city_name,
            v.country_name,
            v.timezone
        FROM Venues v
        INNER JOIN Complexes c ON v.complex_id = c.complex_id
        ORDER BY v.country_name, v.city_name
        """
        return self.execute_query(query)
    
    def get_venues_count_by_complex(self):
        query = """
        SELECT 
            c.complex_name,
            COUNT(*) as venue_count
        FROM Venues v
        INNER JOIN Complexes c ON v.complex_id = c.complex_id
        GROUP BY c.complex_name
        ORDER BY venue_count DESC
        """
        return self.execute_query(query)
    
    def get_venues_by_country(self, country_name):
        query = f"""
        SELECT 
            v.venue_name,
            c.complex_name,
            v.city_name,
            v.timezone
        FROM Venues v
        INNER JOIN Complexes c ON v.complex_id = c.complex_id
        WHERE v.country_name = '{country_name}'
        ORDER BY v.city_name, v.venue_name
        """
        return self.execute_query(query)
    
    def get_all_venues_with_timezones(self):
        query = """
        SELECT 
            v.venue_name,
            v.city_name,
            v.country_name,
            v.timezone
        FROM Venues v
        ORDER BY v.timezone, v.country_name
        """
        return self.execute_query(query)
    
    def get_complexes_with_multiple_venues(self):
        query = """
        SELECT 
            c.complex_name,
            COUNT(*) as venue_count
        FROM Venues v
        INNER JOIN Complexes c ON v.complex_id = c.complex_id
        GROUP BY c.complex_name
        HAVING COUNT(*) > 1
        ORDER BY venue_count DESC
        """
        return self.execute_query(query)
    
    def get_venues_grouped_by_country(self):
        query = """
        SELECT 
            v.country_name,
            COUNT(*) as venue_count
        FROM Venues v
        GROUP BY v.country_name
        ORDER BY venue_count DESC
        """
        return self.execute_query(query)
    
    def get_venues_by_complex(self, complex_name):
        query = f"""
        SELECT 
            v.venue_name,
            v.city_name,
            v.country_name,
            v.timezone
        FROM Venues v
        INNER JOIN Complexes c ON v.complex_id = c.complex_id
        WHERE c.complex_name = '{complex_name}'
        ORDER BY v.venue_name
        """
        return self.execute_query(query)
    
    # ============= COMPETITOR RANKING QUERIES =============
    
    def get_all_competitors_with_rank(self):
        query = """
        SELECT 
            c.name,
            c.country,
            cr.rank,
            cr.points,
            cr.movement,
            cr.competitions_played
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.rank
        """
        return self.execute_query(query)
    
    def get_top_n_competitors(self, n=5):
        query = f"""
        SELECT TOP {n}
            c.name,
            c.country,
            cr.rank,
            cr.points,
            cr.movement
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.rank
        """
        return self.execute_query(query)
    
    def get_stable_rank_competitors(self):
        query = """
        SELECT 
            c.name,
            c.country,
            cr.rank,
            cr.points
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE cr.movement = 0
        ORDER BY cr.rank
        """
        return self.execute_query(query)
    
    def get_country_total_points(self, country_name):
        query = f"""
        SELECT 
            SUM(cr.points) as total_points
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE c.country = '{country_name}'
        """
        return self.execute_query(query)
    
    def get_competitors_per_country(self):
        query = """
        SELECT 
            c.country,
            COUNT(*) as competitor_count,
            AVG(cr.points) as avg_points
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        GROUP BY c.country
        ORDER BY competitor_count DESC
        """
        return self.execute_query(query)
    
    def get_highest_points_competitors(self):
        query = """
        SELECT TOP 10
            c.name,
            c.country,
            cr.rank,
            cr.points,
            cr.movement
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        ORDER BY cr.points DESC
        """
        return self.execute_query(query)
    
    def search_competitor(self, name):
        query = f"""
        SELECT 
            c.name,
            c.country,
            cr.rank,
            cr.points,
            cr.movement,
            cr.competitions_played
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE c.name LIKE '%{name}%'
        ORDER BY cr.rank
        """
        return self.execute_query(query)
    
    def filter_competitors(self, rank_min=None, rank_max=None, country=None, points_min=None):
        conditions = []
        if rank_min:
            conditions.append(f"cr.rank >= {rank_min}")
        if rank_max:
            conditions.append(f"cr.rank <= {rank_max}")
        if country:
            conditions.append(f"c.country = '{country}'")
        if points_min:
            conditions.append(f"cr.points >= {points_min}")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        query = f"""
        SELECT 
            c.name,
            c.country,
            cr.rank,
            cr.points,
            cr.movement,
            cr.competitions_played
        FROM Competitors c
        INNER JOIN Competitor_Rankings cr ON c.competitor_id = cr.competitor_id
        WHERE {where_clause}
        ORDER BY cr.rank
        """
        return self.execute_query(query)
    
    # ============= DASHBOARD STATS =============
    
    def get_dashboard_stats(self):
        query = """
        SELECT 
            (SELECT COUNT(*) FROM Competitors) as total_competitors,
            (SELECT COUNT(DISTINCT country) FROM Competitors) as total_countries,
            (SELECT MAX(points) FROM Competitor_Rankings) as highest_points,
            (SELECT COUNT(*) FROM Competitions) as total_competitions,
            (SELECT COUNT(*) FROM Venues) as total_venues
        """
        return self.execute_query(query)
    
    def get_all_countries(self):
        query = """
        SELECT DISTINCT country 
        FROM Competitors 
        ORDER BY country
        """
        return self.execute_query(query)
    
    def get_all_categories(self):
        query = """
        SELECT DISTINCT category_name 
        FROM Categories 
        ORDER BY category_name
        """
        return self.execute_query(query)
    
    def get_all_complexes(self):
        query = """
        SELECT DISTINCT complex_name 
        FROM Complexes 
        ORDER BY complex_name
        """
        return self.execute_query(query)