# Report 001: Crown Width Implementation

## Overview
This report documents the implementation of crown width calculations in the FVS Python port. Crown width is a critical component used in calculating Crown Competition Factor (CCF) and Percent Canopy Cover (PCC), which affect crown ratios and tree growth through competition effects.

## Implementation Details

### 1. Core Modules
- `crown_width.py`: Contains the fundamental equations and direct database interactions
- `crown_width_calculator.py`: Provides the interface between database and equations

### 2. Database Integration
Two main tables in `fvspy.db`:
- `crown_width_forest_grown`: Coefficients for forest-grown trees
- `crown_width_open_grown`: Coefficients for open-grown trees

### 3. Equation Types

#### Forest-Grown Equations
1. Bechtold equation (2003)
   - Uses 5 coefficients (a1-a5)
   - Applied when dbh ≥ 5 inches
   - Scaled proportionally for dbh < 5 inches

2. Bragg equation (2001)
   - Uses 3 coefficients (a1-a3)
   - Applied when dbh ≥ 5 inches
   - Scaled proportionally for dbh < 5 inches

#### Open-Grown Equations
1. Elk equation (2003)
   - Uses 3 coefficients (a1-a3)
   - Applied when dbh ≥ 3 inches
   - Scaled proportionally for dbh < 3 inches

2. Krajicek equation (1961)
   - Uses 2 coefficients (a1-a2)
   - Applied when dbh ≥ 3 inches
   - Scaled proportionally for dbh < 3 inches

3. Smith equation (1992)
   - Uses 3 coefficients (a1-a3)
   - Applied when dbh ≥ 3 inches
   - Scaled proportionally for dbh < 3 inches

### 4. Key Features
- Proper handling of NULL coefficients in database
- Conversion of numpy types to Python types
- Non-negative crown width enforcement
- Comprehensive test coverage
- Clean separation of concerns between modules

### 5. Testing
Test suite includes verification of:
- Hopkins index calculation
- Forest-grown crown width calculations
- Open-grown crown width calculations
- Crown area calculations
- Database coefficient loading
- Small tree handling (dbh below thresholds)

## Usage in Growth Model
Crown width calculations are used to:
1. Compute Crown Competition Factor (CCF)
2. Calculate Percent Canopy Cover (PCC)
3. Model competition effects on tree growth

## Future Work
1. Add more species-specific coefficients to database
2. Implement additional validation checks
3. Add performance optimizations for large datasets
4. Expand test coverage with more edge cases 