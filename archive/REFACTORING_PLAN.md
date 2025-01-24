# Refactoring Plan: Single Stand Loblolly Pine Simulator

## Goal
Create a simplified simulator that grows a single stand of loblolly pine from planting to maturity (50 years), producing a yield table with trees per acre and volume at 5-year intervals, with visualization capabilities to validate growth patterns.

## Simplification Strategy
1. Remove database dependencies
2. Hard-code loblolly pine parameters
3. Focus on core growth equations
4. Generate simple yield table output

## File Structure
```
src/
├── main.py              # Entry point, runs simulation
├── tree.py             # Tree class and growth equations
├── stand.py            # Stand class and stand-level calculations
├── parameters.py       # Hard-coded loblolly parameters
├── mortality.py        # Mortality models and calculations
└── visualization/      # Visualization tools
    ├── __init__.py
    ├── growth_plots.py      # Growth trajectory plots
    └── stand_plots.py       # Stand-level metric plots
```

## Component Details

### 1. parameters.py
- Hard-code all loblolly pine coefficients:
  - Height-diameter relationship (Curtis-Arney)
  - Crown ratio parameters
  - Growth model coefficients
  - Mortality model parameters
  - Remove all other species parameters

### 2. tree.py
Core functionality:
- Tree class with attributes:
  - DBH
  - Height
  - Crown ratio
  - Age
- Growth methods:
  - Height growth (small trees)
  - Diameter growth (large trees)
  - Crown ratio update
  - Transition zone calculations

### 3. stand.py
Core functionality:
- Stand class managing collection of trees
- Competition calculations
- Stand-level metrics:
  - Trees per acre
  - Basal area
  - Volume calculations
- Integration with mortality models

### 4. mortality.py
Core functionality:
- Individual tree mortality probability
- Stand-level density-dependent mortality
- Competition-induced mortality
- Background mortality rate calculations

### 5. visualization/
Core functionality:
- Growth trajectory plots:
  - Height vs age
  - DBH vs age
  - Volume vs age
- Stand development plots:
  - Trees per acre over time
  - Basal area progression
  - Mortality patterns
- Competition and density plots

### 6. main.py
Streamlined simulation:
1. Initialize stand (500 trees/acre)
2. Run 50-year simulation
3. Generate visualizations
4. Output yield table

## Implementation Steps

1. **Create parameters.py**
   - Extract loblolly coefficients from current codebase
   - Include mortality parameters
   - Organize into clear constant groups

2. **Implement tree.py**
   - Port core growth equations
   - Remove database dependencies
   - Simplify growth calculations

3. **Implement mortality.py**
   - Port essential mortality models
   - Integrate competition effects
   - Calibrate for loblolly pine

4. **Implement stand.py**
   - Focus on essential stand metrics
   - Integrate mortality calculations
   - Calculate competition effects

5. **Implement visualization/**
   - Create core plotting functions
   - Focus on growth validation
   - Add stand density visualizations

6. **Create main.py**
   - Simple command-line interface
   - Generate plots and CSV yield table

## Code to Remove
- Database utilities
- Multiple species handling
- Economic calculations
- Site variation handling
- Unnecessary complexity in mortality models

## Expected Output
1. CSV yield table with columns:
   - Age (5-year intervals)
   - Trees per acre
   - Average DBH
   - Average height
   - Total volume (cubic feet)
   - Mortality rate

2. Visualization plots:
   - Growth trajectories
   - Stand density over time
   - Mortality patterns
   - Competition effects

## Success Criteria
1. Code runs without external dependencies
2. Produces biologically reasonable growth patterns
3. Realistic mortality progression
4. Matches expected loblolly pine growth trajectory
5. Clear, interpretable visualizations
6. Simple, readable implementation
7. Well-documented equations and parameters

## Next Steps
1. Create new files with minimal implementations
2. Port essential equations and parameters
3. Implement mortality models
4. Create visualization functions
5. Test growth and mortality patterns
6. Generate and validate yield table
7. Document assumptions and limitations 