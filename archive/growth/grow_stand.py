import pandas as pd
import numpy as np
from src import growth_models, data_handling, crown_ratio, volume
from typing import List, Dict, Any

def grow_stand(stand: List[Any], projection_period: int, species_data: Dict[str, Any], species_crown_data: Dict[str, Any]) -> pd.DataFrame:
    """Simulates stand growth over a given projection period.

    Args:
        stand: A list of tree objects representing the stand.
        projection_period: The total projection period in years.
        species_data: Dictionary of species specific data.
        species_crown_data: Dictionary of species specific crown data.

    Returns:
        A pandas DataFrame containing stand metrics at each time step.
    """

    stand_history = []
    for year in range(0, projection_period + 5, 5):  # Iterate in 5-year steps
        stand_metrics = {"year": year, "total_volume": 0, "basal_area": 0, "trees_per_acre": 0}
        for tree in stand:
            try:
                if tree.dbh < 3.0:  # Small tree growth
                    if tree.height is None:
                        tree.height = 4.5
                    tree.small_tree_height_growth = growth_models.calculate_small_tree_height_growth(
                        tree.si, tree.age, 
                        species_data[tree.species]["SmallTreeGrowth_c1"], 
                        species_data[tree.species]["SmallTreeGrowth_c2"], 
                        species_data[tree.species]["SmallTreeGrowth_c3"], 
                        species_data[tree.species]["SmallTreeGrowth_c4"], 
                        species_data[tree.species]["SmallTreeGrowth_c5"], 
                        tree.height
                    )
                    ht_start = tree.height
                    if species_data[tree.species]["CurtisArney_b0"] is not None:
                        tree.dbh = (np.log(species_data[tree.species]["CurtisArney_b1"]/(ht_start-species_data[tree.species]["CurtisArney_b0"]))/-species_data[tree.species]["CurtisArney_b2"])
                    elif species_data[tree.species]["Wykoff_b0"] is not None:
                        #Solve for dbh using the wykoff equation. This requires numerical methods.
                        pass #Placeholder for now.
                    bark_thickness = growth_models.calculate_bark_thickness(tree.dbh, species_data[tree.species]["BarkThickness_a"], species_data[tree.species]["BarkThickness_b"])
                    dbh_ib = growth_models.calculate_inside_bark_dbh(tree.dbh, bark_thickness)
                    tree.height = tree.small_tree_height_growth
                else:  # Large tree growth
                    acr = crown_ratio.calculate_acr(tree.RELSDI, tree.species)
                    a, b, c = crown_ratio.calculate_weibull_parameters(acr, species_crown_data[tree.species]["a"], species_crown_data[tree.species]["b0"], species_crown_data[tree.species]["b1"], species_crown_data[tree.species]["c"])
                    scale = crown_ratio.calculate_scale(tree.CCF)
                    x = 0.5 #Placeholder
                    new_cr = crown_ratio.calculate_crown_ratio_weibull(x, a, b, c, scale)
                    tree.large_tree_diameter_growth = growth_models.calculate_large_tree_diameter_growth(tree.dbh, new_cr/100, tree.RELHT, tree.SI, tree.BA, tree.PBAL, tree.Slope, tree.Aspect, tree.Fortype, tree.Ecounit, tree.Plant, {k.replace('LargeTreeGrowth_', ''): v for k, v in species_data[tree.species].items() if k.startswith('LargeTreeGrowth_')}, species_data[tree.species]["Lower_Diameter_Limit"], species_data[tree.species]["Upper_Diameter_Limit"])
                    tree.dbh += tree.large_tree_diameter_growth
                    bark_thickness = growth_models.calculate_bark_thickness(tree.dbh, species_data[tree.species]["BarkThickness_a"], species_data[tree.species]["BarkThickness_b"])
                    dbh_ib = growth_models.calculate_inside_bark_dbh(tree.dbh, bark_thickness)
                    tree.height = growth_models.curtis_arney(tree.dbh, species_data[tree.species]["CurtisArney_b0"], species_data[tree.species]["CurtisArney_b1"], species_data[tree.species]["CurtisArney_b2"])

                tree.age += 5
                tree.volume = volume.calculate_tree_volume(tree.species, tree.dbh, tree.height, species_data[tree.species]["Volume_b0"], species_data[tree.species]["Volume_b1"], species_data[tree.species]["Volume_b2"])
                stand_metrics["total_volume"] += tree.volume * tree.trees_per_acre
                stand_metrics["basal_area"] += (np.pi*(tree.dbh/2)**2) * tree.trees_per_acre/144
                stand_metrics["trees_per_acre"] += tree.trees_per_acre
            except KeyError as e:
                print(f"KeyError in growth loop: {e}. Check if the key exists in species data for species: {tree.species}")
                continue #Skip the rest of the calculations for this tree and move onto the next

        stand_history.append(stand_metrics)

    return pd.DataFrame(stand_history)