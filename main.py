import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

class MeterReading:
    def __init__(self, timestamp, kwh):
        self.timestamp = timestamp
        self.kwh = kwh

class Building:
    def __init__(self, name):
        self.name = name
        self.readings = []

    def add_reading(self, reading):
        self.readings.append(reading)

class BuildingManager:
    def __init__(self):
        self.buildings = {}

    def get_building(self, name):
        if name not in self.buildings:
            self.buildings[name] = Building(name)
        return self.buildings[name]

def load_data(data_dir):
    all_files = list(Path(data_dir).glob('*.csv'))
    combined_df = pd.DataFrame()
    manager = BuildingManager()

    for file in all_files:
        try:
            building_name = file.stem
            df = pd.read_csv(file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['building'] = building_name
            
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
            building_obj = manager.get_building(building_name)
            for _, row in df.iterrows():
                reading = MeterReading(row['timestamp'], row['kwh'])
                building_obj.add_reading(reading)

        except Exception as e:
            print(f"Error reading {file}: {e}")

    return combined_df, manager

def generate_visualizations(df):
    if df.empty:
        print("No data to visualize.")
        return

    plt.figure(figsize=(15, 10))

    plt.subplot(2, 2, 1)
    daily = df.groupby([df['timestamp'].dt.date, 'building'])['kwh'].sum().unstack()
    daily.plot(ax=plt.gca())
    plt.title('Daily Consumption Trends')
    plt.ylabel('Total kWh')
    plt.grid(True)

    plt.subplot(2, 2, 2)
    weekly_avg = df.groupby('building')['kwh'].mean()
    weekly_avg.plot(kind='bar', color='skyblue', ax=plt.gca())
    plt.title('Average Usage per Building')
    plt.ylabel('Avg kWh')

    plt.subplot(2, 1, 2)
    plt.scatter(df['timestamp'], df['kwh'], c='orange', alpha=0.5)
    plt.title('Consumption Events')
    plt.xlabel('Time')
    plt.ylabel('kWh Reading')

    plt.tight_layout()
    plt.savefig('output/dashboard.png')
    print("Dashboard saved to output/dashboard.png")

def save_summary(df):
    if df.empty:
        return

    df.to_csv('output/cleaned_energy_data.csv', index=False)
    
    summary = df.groupby('building')['kwh'].agg(['sum', 'mean', 'min', 'max'])
    summary.to_csv('output/building_summary.csv')

    total_consumption = df['kwh'].sum()
    highest_building = summary['sum'].idxmax()
    peak_time = df.loc[df['kwh'].idxmax(), 'timestamp']

    report = f"""
    CAMPUS ENERGY REPORT
    ====================
    Total Consumption: {total_consumption:.2f} kWh
    Highest Consuming Building: {highest_building}
    Peak Load Time: {peak_time}
    """
    
    with open('output/summary.txt', 'w') as f:
        f.write(report)
    
    print(report)

def main():
    os.makedirs('output', exist_ok=True)
    
    print("Loading data...")
    df, manager = load_data('data')
    
    if not df.empty:
        print("Generating visualizations...")
        generate_visualizations(df)
        
        print("Saving reports...")
        save_summary(df)
        print("Done!")
    else:
        print("No data found in /data/ folder.")

if __name__ == "__main__":
    main()