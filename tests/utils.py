"""
Utilities for test visualization and reporting.
"""
import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import base64
from io import BytesIO
from datetime import datetime

def setup_test_output():
    """Create test output directory structure."""
    output_dir = Path(__file__).parent.parent / 'test_output'
    for subdir in ['tree_tests', 'stand_tests']:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)
    return output_dir

def plot_tree_growth_comparison(trees_over_time, title, save_path):
    """Plot growth comparison between multiple trees over time.
    
    Args:
        trees_over_time: List of (metrics_list, label) tuples where metrics_list contains
                        tree measurements at different ages
        title: Plot title
        save_path: Path to save plot
    
    Returns:
        str: Base64 encoded image for embedding in markdown
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title)
    
    # Plot DBH over time
    for metrics, label in trees_over_time:
        ages = [m['age'] for m in metrics]
        dbhs = [m['dbh'] for m in metrics]
        ax1.plot(ages, dbhs, 'o-', label=label)
    ax1.set_xlabel('Age (years)')
    ax1.set_ylabel('DBH (inches)')
    ax1.grid(True)
    ax1.legend()
    
    # Plot Height over time
    for metrics, label in trees_over_time:
        ages = [m['age'] for m in metrics]
        heights = [m['height'] for m in metrics]
        ax2.plot(ages, heights, 'o-', label=label)
    ax2.set_xlabel('Age (years)')
    ax2.set_ylabel('Height (feet)')
    ax2.grid(True)
    ax2.legend()
    
    plt.tight_layout()
    
    # Save to file
    plt.savefig(save_path)
    
    # Save to buffer for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Encode
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

def plot_stand_development(metrics_list, labels, title, save_path):
    """Plot stand development metrics over time.
    
    Args:
        metrics_list: List of metric dictionaries over time
        labels: List of labels for each metric set
        title: Plot title
        save_path: Path to save plot
    
    Returns:
        str: Base64 encoded image for embedding in markdown
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title)
    
    for metrics, label in zip(metrics_list, labels):
        ages = [m['age'] for m in metrics]
        
        # TPA over time
        ax1.plot(ages, [m['tpa'] for m in metrics], 'o-', label=label)
        ax1.set_xlabel('Age (years)')
        ax1.set_ylabel('Trees per Acre')
        ax1.grid(True)
        
        # Mean DBH over time
        ax2.plot(ages, [m['mean_dbh'] for m in metrics], 'o-', label=label)
        ax2.set_xlabel('Age (years)')
        ax2.set_ylabel('Mean DBH (inches)')
        ax2.grid(True)
        
        # Mean Height over time
        ax3.plot(ages, [m['mean_height'] for m in metrics], 'o-', label=label)
        ax3.set_xlabel('Age (years)')
        ax3.set_ylabel('Mean Height (feet)')
        ax3.grid(True)
        
        # Volume over time
        ax4.plot(ages, [m['volume'] for m in metrics], 'o-', label=label)
        ax4.set_xlabel('Age (years)')
        ax4.set_ylabel('Volume (cu ft/acre)')
        ax4.grid(True)
    
    for ax in (ax1, ax2, ax3, ax4):
        ax.legend()
    
    plt.tight_layout()
    
    # Save to file
    plt.savefig(save_path)
    
    # Save to buffer for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Encode
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

def plot_long_term_growth(metrics, title, save_path):
    """Plot long-term growth metrics with separate panels for each metric.
    
    Args:
        metrics: List of metric dictionaries containing measurements over time
        title: Plot title
        save_path: Path to save plot
    
    Returns:
        str: Base64 encoded image for embedding in markdown
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title)
    
    ages = [m['age'] for m in metrics]
    
    # DBH over time
    dbhs = [m['dbh'] for m in metrics]
    ax1.plot(ages, dbhs, 'o-', label='DBH')
    ax1.set_xlabel('Age (years)')
    ax1.set_ylabel('DBH (inches)')
    ax1.grid(True)
    
    # Height over time
    heights = [m['height'] for m in metrics]
    ax2.plot(ages, heights, 'o-', label='Height')
    ax2.set_xlabel('Age (years)')
    ax2.set_ylabel('Height (feet)')
    ax2.grid(True)
    
    # Volume over time
    volumes = [m['volume'] for m in metrics]
    ax3.plot(ages, volumes, 'o-', label='Volume')
    ax3.set_xlabel('Age (years)')
    ax3.set_ylabel('Volume (cu ft)')
    ax3.grid(True)
    
    # Growth rates
    dbh_growth = [0] + [(dbhs[i] - dbhs[i-1]) for i in range(1, len(dbhs))]
    height_growth = [0] + [(heights[i] - heights[i-1]) for i in range(1, len(heights))]
    
    ax4.plot(ages, dbh_growth, 'o-', label='DBH Growth')
    ax4.plot(ages, height_growth, 'o-', label='Height Growth')
    ax4.set_xlabel('Age (years)')
    ax4.set_ylabel('Annual Growth (DBH: inches, Height: feet)')
    ax4.grid(True)
    ax4.legend()
    
    for ax in (ax1, ax2, ax3):
        ax.legend()
    
    plt.tight_layout()
    
    # Save to file
    plt.savefig(save_path)
    
    # Save to buffer for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Encode
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

def plot_long_term_stand_growth(metrics, title, save_path):
    """Plot long-term stand development metrics with separate panels for each metric.
    
    Args:
        metrics: List of metric dictionaries containing measurements over time
        title: Plot title
        save_path: Path to save plot
    
    Returns:
        str: Base64 encoded image for embedding in markdown
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle(title)
    
    ages = [m['age'] for m in metrics]
    
    # Trees per acre over time
    tpa = [m['tpa'] for m in metrics]
    ax1.plot(ages, tpa, 'o-', label='Trees per Acre')
    ax1.set_xlabel('Age (years)')
    ax1.set_ylabel('Trees per Acre')
    ax1.grid(True)
    
    # Mean DBH and height over time
    mean_dbh = [m['mean_dbh'] for m in metrics]
    mean_height = [m['mean_height'] for m in metrics]
    ax2.plot(ages, mean_dbh, 'o-', label='Mean DBH')
    ax2.plot(ages, mean_height, 'o-', label='Mean Height')
    ax2.set_xlabel('Age (years)')
    ax2.set_ylabel('Size (DBH: inches, Height: feet)')
    ax2.grid(True)
    ax2.legend()
    
    # Volume over time
    volumes = [m['volume'] for m in metrics]
    ax3.plot(ages, volumes, 'o-', label='Volume')
    ax3.set_xlabel('Age (years)')
    ax3.set_ylabel('Volume (cu ft/acre)')
    ax3.grid(True)
    
    # Growth rates
    tpa_change = [0] + [(tpa[i-1] - tpa[i]) for i in range(1, len(tpa))]  # Mortality
    dbh_growth = [0] + [(mean_dbh[i] - mean_dbh[i-1]) for i in range(1, len(mean_dbh))]
    height_growth = [0] + [(mean_height[i] - mean_height[i-1]) for i in range(1, len(mean_height))]
    
    ax4.plot(ages, tpa_change, 'o-', label='Mortality (trees/year)')
    ax4.plot(ages, dbh_growth, 'o-', label='DBH Growth (in/year)')
    ax4.plot(ages, height_growth, 'o-', label='Height Growth (ft/year)')
    ax4.set_xlabel('Age (years)')
    ax4.set_ylabel('Annual Change')
    ax4.grid(True)
    ax4.legend()
    
    for ax in (ax1, ax2, ax3):
        ax.legend()
    
    plt.tight_layout()
    
    # Save to file
    plt.savefig(save_path)
    
    # Save to buffer for embedding
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    
    # Encode
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return img_base64

def generate_test_report(test_name, results, save_path, plot_base64=None):
    """Generate Markdown report for test results.
    
    Args:
        test_name: Name of the test
        results: Dictionary or list of test results
        save_path: Path to save markdown report
        plot_base64: Optional base64 encoded plot to embed
    """
    # Convert results to DataFrame for table formatting
    if isinstance(results, list):
        df = pd.DataFrame(results)
    else:
        df = pd.DataFrame([results])
    
    # Convert DataFrame to markdown table
    table = df.to_markdown(index=False)
    
    # Create markdown content with forestry context
    markdown = f"""# {test_name}
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Purpose
This test validates the growth model's behavior for {test_name.lower()}.

## Expected Relationships
Based on established forestry principles:

"""
    
    # Add test-specific expectations
    if "Small Tree" in test_name:
        markdown += """- Height growth should be rapid in early years
- DBH growth should increase with tree size
- Crown ratio should remain high (>0.5) in young trees
- Growth rates should be sensitive to site index"""
    elif "Large Tree" in test_name:
        markdown += """- Height growth should slow with age
- DBH growth should be more consistent
- Crown ratio should decrease with increasing competition
- Growth should be more sensitive to competition than site index"""
    elif "Competition" in test_name:
        markdown += """- Higher competition should reduce both height and diameter growth
- Crown ratio should decrease with increasing competition
- Effect should be more pronounced on diameter than height growth
- Growth reduction should be proportional to competition intensity"""
    elif "Long-term" in test_name:
        markdown += """- Height growth should follow a sigmoid curve
- DBH growth should be more linear
- Volume growth should be exponential initially, then level off
- Crown ratio should decrease with age
- Growth patterns should reflect site quality differences"""
    
    markdown += f"""

## Test Results

{table}
"""
    
    # Add visualization if provided
    if plot_base64:
        markdown += f"""
## Visualization

![{test_name} Visualization](data:image/png;base64,{plot_base64})

### Interpretation
The plots show the development of key tree/stand metrics over time. The trajectories should follow expected biological growth patterns and respond appropriately to environmental factors (site index, competition).
"""
    
    # Save with .md extension
    save_path = save_path.with_suffix('.md')
    with open(save_path, 'w') as f:
        f.write(markdown) 