import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import List, Dict, Any
from . import growth_models, crown_ratio
import os

def visualize_stand_growth(stand_history, output_dir, plot_id):
    """Visualize stand growth over time.
    
    Args:
        stand_history: DataFrame containing stand metrics over time
        output_dir: Directory to save plots
        plot_id: Plot ID for labeling
    """
    # Set up the plotting style
    plt.style.use('default')
    
    # Create a figure with multiple subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Plot average DBH over time
    ax1.plot(stand_history['year'], stand_history['avg_dbh'], marker='o')
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Average DBH (inches)')
    ax1.set_title('Average DBH Over Time')
    ax1.grid(True)
    
    # Plot average height over time
    ax2.plot(stand_history['year'], stand_history['avg_height'], marker='o')
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Average Height (feet)')
    ax2.set_title('Average Height Over Time')
    ax2.grid(True)
    
    # Plot basal area over time
    ax3.plot(stand_history['year'], stand_history['basal_area'], marker='o')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Basal Area (sq ft/acre)')
    ax3.set_title('Basal Area Over Time')
    ax3.grid(True)
    
    # Plot trees per acre over time
    ax4.plot(stand_history['year'], stand_history['trees_per_acre'], marker='o')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Trees per Acre')
    ax4.set_title('Trees per Acre Over Time')
    ax4.grid(True)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'stand_growth_{plot_id}.png'))
    plt.close()

def visualize_dbh_distribution(stand: List[Any], year: int):
    """Visualizes the DBH distribution of the stand at a given year.
    
    Args:
        stand: List of tree objects
        year: Current projection year
    """
    # Weight DBH values by trees per acre
    dbhs = []
    for tree in stand:
        dbhs.extend([tree.dbh] * int(tree.trees_per_acre))
    
    plt.figure(figsize=(10, 6))
    sns.histplot(dbhs, kde=True, bins=30)
    plt.xlabel("DBH (inches)")
    plt.ylabel("Frequency (trees per acre)")
    plt.title(f"DBH Distribution at Year {year}")
    plt.show()

def visualize_height_distribution(stand: List[Any], year: int):
    """Visualizes the height distribution of the stand at a given year.
    
    Args:
        stand: List of tree objects
        year: Current projection year
    """
    # Weight height values by trees per acre
    heights = []
    for tree in stand:
        heights.extend([tree.height] * int(tree.trees_per_acre))
    
    plt.figure(figsize=(10, 6))
    sns.histplot(heights, kde=True, bins=30)
    plt.xlabel("Height (feet)")
    plt.ylabel("Frequency (trees per acre)")
    plt.title(f"Height Distribution at Year {year}")
    plt.show()

def visualize_tree_attributes(stand: List[Any], year: int):
    """Visualizes the relationship between DBH and Height.
    
    Args:
        stand: List of tree objects
        year: Current projection year
    """
    # Create scatter plot with point size proportional to trees per acre
    dbhs = [tree.dbh for tree in stand]
    heights = [tree.height for tree in stand]
    sizes = [tree.trees_per_acre * 10 for tree in stand]  # Scale TPA for visualization
    
    plt.figure(figsize=(10, 6))
    plt.scatter(dbhs, heights, s=sizes, alpha=0.5)
    plt.xlabel("DBH (inches)")
    plt.ylabel("Height (feet)")
    plt.title(f"DBH vs. Height at Year {year}\n(Point size proportional to trees per acre)")
    
    # Add trend line
    z = np.polyfit(dbhs, heights, 1)
    p = np.poly1d(z)
    plt.plot(dbhs, p(dbhs), "r--", alpha=0.8, label="Trend line")
    plt.legend()
    
    plt.show()

def visualize_species_composition(stand: List[Any], year: int):
    """Visualizes the species composition of the stand.
    
    Args:
        stand: List of tree objects
        year: Current projection year
    """
    # Calculate basal area by species
    species_ba = {}
    for tree in stand:
        ba = (np.pi * (tree.dbh/2)**2 * tree.trees_per_acre) / 144
        species_ba[tree.species] = species_ba.get(tree.species, 0) + ba
    
    # Create pie chart
    plt.figure(figsize=(10, 6))
    plt.pie(species_ba.values(), labels=species_ba.keys(), autopct='%1.1f%%')
    plt.title(f"Species Composition by Basal Area at Year {year}")
    plt.show()

def create_stand_summary(stand: List[Any]) -> pd.DataFrame:
    """Creates a summary DataFrame of stand metrics.
    
    Args:
        stand: List of tree objects
        
    Returns:
        DataFrame containing stand summary statistics
    """
    species_data = {}
    for tree in stand:
        if tree.species not in species_data:
            species_data[tree.species] = {
                'tpa': 0,
                'ba': 0,
                'qmd': [],
                'avg_height': [],
                'min_dbh': float('inf'),
                'max_dbh': float('-inf')
            }
        
        tpa = tree.trees_per_acre
        species_data[tree.species]['tpa'] += tpa
        species_data[tree.species]['ba'] += (np.pi * (tree.dbh/2)**2 * tpa) / 144
        species_data[tree.species]['qmd'].append((tree.dbh**2) * tpa)
        species_data[tree.species]['avg_height'].append(tree.height * tpa)
        species_data[tree.species]['min_dbh'] = min(species_data[tree.species]['min_dbh'], tree.dbh)
        species_data[tree.species]['max_dbh'] = max(species_data[tree.species]['max_dbh'], tree.dbh)
    
    # Calculate final metrics
    summary_data = []
    for species, data in species_data.items():
        qmd = np.sqrt(sum(data['qmd']) / data['tpa'])
        avg_height = sum(data['avg_height']) / data['tpa']
        
        summary_data.append({
            'Species': species,
            'Trees per Acre': data['tpa'],
            'Basal Area (sq ft/acre)': data['ba'],
            'QMD (inches)': qmd,
            'Average Height (ft)': avg_height,
            'Min DBH (inches)': data['min_dbh'],
            'Max DBH (inches)': data['max_dbh']
        })
    
    return pd.DataFrame(summary_data)