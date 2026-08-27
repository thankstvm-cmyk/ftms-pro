import sqlite3
class DashboardSummary:
    def __init__(self, db_name="ftms.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        
    def get_vehicle_summary(self):
        #TOTAL VEHICLES
        summary = {}
        self.cursor.execute("SELECT COUNT(*) FROM vehicles")
        summary["total_vehicles"] = self.cursor.fetchone()[0]
        # VEHICLE COUNT BY CATEGORY
        self.cursor.execute(""" SELECT ton_capacity, COUNT(*) FROM vehicles GROUP BY ton_capacity HAVING COUNT(*)>0 ORDER BY COUNT(*) DESC """)
        summary["fleet_summary"] = self.cursor.fetchall()
        
        #LARGEST FLEET
        if summary["fleet_summary"]: 
            summary["largest_fleet"] = summary["fleet_summary"][0]
        else:
            summary["largest_fleet"][0] = ("No Vehicles",0)
        return summary