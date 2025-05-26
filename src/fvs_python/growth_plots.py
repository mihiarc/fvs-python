"""
Visualization functions for growth trajectories and stand metrics.
"""
import matplotlib.pyplot as plt
import numpy as np

def plot_stand_trajectories(metrics_over_time, save_path=None):
    """Plot key stand metrics over time.
    
    Args:
        metrics_over_time: List of dictionaries containing stand metrics at each age
        save_path: Optional path to save the plot
    """
    # Extract time series
    ages = [m['age'] for m in metrics_over_time]
    tpa = [m['tpa'] for m in metrics_over_time]
    volume = [m['volume'] for m in metrics_over_time]
    mean_height = [m['mean_height'] for m in metrics_over_time]
    mean_dbh = [m['mean_dbh'] for m in metrics_over_time]
    basal_area = [m['basal_area'] for m in metrics_over_time]
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Stand Development Trajectories', fontsize=14)
    
    # Trees per acre
    ax1.plot(ages, tpa, 'b-', label='Trees per Acre')
    ax1.set_xlabel('Stand Age (years)')
    ax1.set_ylabel('Trees per Acre')
    ax1.grid(True)
    
    # Volume
    ax2.plot(ages, volume, 'g-', label='Volume')
    ax2.set_xlabel('Stand Age (years)')
    ax2.set_ylabel('Volume (cubic feet/acre)')
    ax2.grid(True)
    
    # Mean tree size
    ax3.plot(ages, mean_height, 'r-', label='Height')
    ax3.plot(ages, mean_dbh, 'b--', label='DBH')
    ax3.set_xlabel('Stand Age (years)')
    ax3.set_ylabel('Tree Size (feet/inches)')
    ax3.legend()
    ax3.grid(True)
    
    # Basal area
    ax4.plot(ages, basal_area, 'k-', label='Basal Area')
    ax4.set_xlabel('Stand Age (years)')
    ax4.set_ylabel('Basal Area (sq ft/acre)')
    ax4.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    
    plt.close()

def plot_size_distributions(stand, save_path=None):
    """Plot current DBH and height distributions.
    
    Args:
        stand: Stand object
        save_path: Optional path to save the plot
    """
    if not stand.trees:
        return
    
    # Get tree data
    dbhs = [tree.dbh for tree in stand.trees]
    heights = [tree.height for tree in stand.trees]
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Stand Size Distributions at Age {stand.age}', fontsize=14)
    
    # DBH distribution
    ax1.hist(dbhs, bins=20, edgecolor='black')
    ax1.set_xlabel('DBH (inches)')
    ax1.set_ylabel('Number of Trees')
    ax1.set_title('DBH Distribution')
    ax1.grid(True)
    
    # Height distribution
    ax2.hist(heights, bins=20, edgecolor='black')
    ax2.set_xlabel('Height (feet)')
    ax2.set_ylabel('Number of Trees')
    ax2.set_title('Height Distribution')
    ax2.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    
    plt.close()

def plot_mortality_patterns(metrics_over_time, save_path=None):
    """Plot mortality patterns over time.
    
    Args:
        metrics_over_time: List of dictionaries containing stand metrics at each age
        save_path: Optional path to save the plot
    """
    # Extract time series
    ages = [m['age'] for m in metrics_over_time]
    tpa = [m['tpa'] for m in metrics_over_time]
    
    # Calculate mortality rate
    mortality_rates = []
    for i in range(1, len(tpa)):
        rate = (tpa[i-1] - tpa[i]) / tpa[i-1] if tpa[i-1] > 0 else 0
        mortality_rates.append(rate)
    
    # Create plot
    plt.figure(figsize=(10, 6))
    plt.plot(ages[1:], mortality_rates, 'r-', label='Annual Mortality Rate')
    plt.xlabel('Stand Age (years)')
    plt.ylabel('Annual Mortality Rate')
    plt.title('Stand Mortality Patterns')
    plt.grid(True)
    plt.legend()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    
    plt.close()

def plot_competition_effects(stand, save_path=None):
    """Plot relationship between tree size and competition.
    
    Args:
        stand: Stand object
        save_path: Optional path to save the plot
    """
    if not stand.trees:
        return
    
    # Get competition factors
    competition_metrics = stand._calculate_competition_metrics()
    competition_factors = [m['competition_factor'] for m in competition_metrics]
    
    # Get tree data
    dbhs = [tree.dbh for tree in stand.trees]
    heights = [tree.height for tree in stand.trees]
    
    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(f'Competition Effects at Age {stand.age}', fontsize=14)
    
    # DBH vs Competition
    ax1.scatter(dbhs, competition_factors, alpha=0.5)
    ax1.set_xlabel('DBH (inches)')
    ax1.set_ylabel('Competition Factor')
    ax1.set_title('DBH vs Competition')
    ax1.grid(True)
    
    # Height vs Competition
    ax2.scatter(heights, competition_factors, alpha=0.5)
    ax2.set_xlabel('Height (feet)')
    ax2.set_ylabel('Competition Factor')
    ax2.set_title('Height vs Competition')
    ax2.grid(True)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()
    
    plt.close() 