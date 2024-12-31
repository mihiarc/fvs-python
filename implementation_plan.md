# Implementation Plan

## 1. Overview of Stand Growth Process

### Stand Initialization
- Create a new stand by specifying:
  - Species (one of: Loblolly Pine 'LP', Shortleaf Pine 'SP', Longleaf Pine 'LL', or Slash Pine 'SA')
  - Initial trees per acre (TPA)
  - Site index (base age 25)
- Initialization process:
  - Sets initial DBH around 0.5 inches with random variation (SD = 0.1)
  - Sets initial height to 1.0 feet
  - Creates individual tree records for each planted tree
  - Validates inputs against species-specific ranges

### Growth Simulation
- Runs in timesteps (default 5-year intervals) from age 0 to end age (default 50 years)
- For each timestep:
  1. Updates competition between trees
  2. Grows each tree:
     - Calculates potential height growth using Chapman-Richards function
     - Applies competition modifiers
     - Updates tree diameter using species-specific equations
     - Updates crown width and ratio
  3. Applies mortality
  4. Calculates stand metrics:
     - Trees per acre
     - Basal area per acre
     - Volume per acre
     - Quadratic mean diameter
     - Dominant height

### Species Parameters
- Loblolly Pine (LP):
  - TPA: 500-700
  - Site Index: 50-70
  - Typical rotation: 20-30 years
  - Growth coefficients:
    - CurtisArney_b0: 243.860648
    - CurtisArney_b1: 4.28460566
    - CurtisArney_b2: -0.47130185
- Shortleaf Pine (SP):
  - TPA: 400-600
  - Site Index: 45-65
  - Typical rotation: 30-40 years
  - Growth coefficients:
    - CurtisArney_b0: 444.0921666
    - CurtisArney_b1: 4.11876312
    - CurtisArney_b2: -0.30617043
- Longleaf Pine (LL):
  - TPA: 300-500
  - Site Index: 45-65
  - Typical rotation: 35-45 years
  - Growth coefficients:
    - CurtisArney_b0: 98.56082813
    - CurtisArney_b1: 3.89930709
    - CurtisArney_b2: -0.86730393
- Slash Pine (SA):
  - TPA: 450-650
  - Site Index: 50-70
  - Typical rotation: 25-35 years
  - Growth coefficients:
    - CurtisArney_b0: 1087.101439
    - CurtisArney_b1: 5.10450596
    - CurtisArney_b2: -0.24284896

## 2. Project Structure

```
/
├── models/           # Core data structures
│   ├── tree.py      # Tree class with expanded attributes
│   ├── stand.py     # Stand class implementation
│   ├── species.py   # Comprehensive species configuration
│   └── validators.py # Input validation functions
├── data/            # Database and coefficient tables
│   ├── sqlite/      # SQLite database files
│   │   └── fvspy.db # Main database
│   └── coefficients/# Raw coefficient data
├── core/            # Growth engine components
│   ├── growth/      # Growth model implementations
│   │   ├── height_diameter.py
│   │   ├── small_tree.py
│   │   └── large_tree.py
│   ├── crown/       # Crown modeling
│   │   ├── forest_crown.py
│   │   ├── open_crown.py
│   │   └── crown_ratio.py
│   ├── site/        # Site and ecological components
│   │   ├── site_index.py
│   │   └── ecological.py
│   ├── bark/        # Bark thickness calculations
│   ├── competition/ # Competition calculations
│   └── mortality/   # Mortality models
├── simulation/      # Stand growth controllers
│   ├── grow_stand.py
│   └── yield_tables.py
└── analysis/        # Metrics and analysis tools
    ├── metrics.py
    └── visualization.py
```

## 3. Implementation Components

### Core Data Structures (models/)

#### Tree Class
```python
@dataclass
class Tree:
    # Basic attributes
    species_code: str
    dbh: float
    height: float
    
    # Crown attributes
    crown_ratio: float = 0.0
    forest_crown_width: float = 0.0
    open_crown_width: float = 0.0
    
    # Growth tracking
    previous_dbh: Optional[float] = None
    previous_height: Optional[float] = None
    growth_increment: Optional[float] = None
    
    # Competition metrics
    pccf: float = 0.0
    ccf: float = 0.0
    
    # Additional characteristics
    bark_thickness: float = 0.0
    shade_tolerance: str = ''
    ecological_unit: str = ''
    expansion_factor: float = 1.0
```

#### Species Configuration
```python
@dataclass
class SpeciesConfig:
    # Basic info
    code: str
    site_index_range: tuple[float, float]
    dbw: float  # diameter breakpoint
    
    # Growth coefficients
    small_tree_coeffs: Dict[str, float]
    large_tree_coeffs: Dict[str, float]
    curtis_arney_coeffs: Dict[str, float]
    wykoff_coeffs: Dict[str, float]
    
    # Crown and bark
    crown_coeffs_forest: Dict[str, float]
    crown_coeffs_open: Dict[str, float]
    bark_coeffs: Dict[str, float]
    
    # Environmental
    shade_tolerance: str
    ecological_coeffs: Dict[str, float]
    
    # Validation limits
    dbh_limits: tuple[float, float]
    planted_coefficient: float
```

### Database Schema Overview

#### Core Tables
- species (species_code)
- site_index_groups (site_index_species, mapped_species)
- site_index_range (species_code, si_min, si_max, dbw)
- bark_thickness (species_code, bark_b0, bark_b1)

#### Growth Tables
- curtis_arney_functions
- wykoff_functions
- large_tree_growth
- small_tree_growth

#### Crown Tables
- crown_width_forest_grown
- crown_width_open_grown
- species_crown_ratio
- shade_tolerance_by_species
- shade_tolerance_coefficients

#### Environmental Tables
- ecological_units
- ecological_coefficients
- forest_types

## 4. Implementation Phases

### Phase 1: Core Data Structures and Database Access
- [x] Implement expanded Tree class with all attributes
- [x] Implement Stand class with tree management
- [x] Create comprehensive SpeciesConfig
- [x] Build database access layer:
  - [x] Growth coefficient retrieval
  - [x] Crown width calculations
  - [x] Site index conversions
  - [x] Ecological unit management
  - [x] Shade tolerance handling
- [x] Implement validation system:
  - [x] Diameter bounds checking
  - [x] Site index range validation
  - [x] Species code validation
  - [x] Ecological unit validation

### Phase 2: Basic Growth and Crown Models
- [ ] Implement height-diameter relationships:
  - [x] Curtis-Arney equation
  - [ ] Wykoff equation
- [ ] Add Chapman-Richards height growth
- [ ] Create diameter growth calculations
- [ ] Implement crown models:
  - [ ] Forest-grown crown width
  - [ ] Open-grown crown width
  - [ ] Crown ratio calculations
- [ ] Add bark thickness calculations
- [ ] Implement stand initialization

### Phase 3: Environmental and Competition
- [x] Add ecological unit effects
- [x] Implement shade tolerance impacts
- [ ] Create competition indices
- [ ] Add growth modifiers
- [ ] Implement mortality functions
- [ ] Add density-dependent adjustments

### Phase 4: Integration
- [ ] Build main growth controller
- [ ] Add stand metrics calculations
- [ ] Implement volume equations
- [ ] Create site index conversion system
- [ ] Build yield table generation

### Phase 5: Analysis and Validation
- [ ] Add stand-level analysis
- [ ] Create visualization tools
- [ ] Implement validation system:
  - [ ] Compare against FVS outputs
  - [ ] Validate growth patterns
  - [ ] Check ecological responses
- [ ] Add economic analysis

## 5. Best Practices

### Code Organization
- Use type hints throughout
- Follow PEP 8 style guide
- Document all functions with Google-style docstrings
- Use dataclasses for data structures
- Implement proper error handling for database operations

### Testing
- Write unit tests for each module
- Create integration tests for growth cycles
- Add validation against FVS outputs
- Test with real stand data
- Include database operation tests
- Validate ecological responses

### Error Handling
- Use custom exceptions for domain-specific errors
- Validate all inputs against species ranges
- Add comprehensive logging
- Include database error handling
- Validate ecological unit inputs

### Performance
- Use NumPy for numerical operations
- Implement caching for database queries
- Optimize tree list operations
- Profile and optimize critical paths
- Use proper database indexing

### Documentation
- Maintain API documentation
- Include usage examples
- Document all equations and sources
- Add validation results
- Document database schema and relationships
