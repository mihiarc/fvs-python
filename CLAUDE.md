# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Forest Vegetation Simulator (FVS) - Python implementation for simulating growth and yield of southern yellow pine species (Loblolly, Shortleaf, Longleaf, and Slash pine). The project uses an object-oriented architecture with modular growth models.

## Key Development Commands

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fvs_python --cov-report=term-missing

# Run specific test file
pytest tests/test_tree.py

# Run with verbose output and short traceback
pytest -v --tb=short
```

### Code Quality
```bash
# Format code (required before commits)
black src/fvs_python tests

# Lint code
flake8 src/fvs_python tests

# Type checking
mypy src/fvs_python
```

### Running the Application
```bash
# Install in development mode
pip install -e .

# Run simulation via CLI
fvs-simulate run --years 50 --species LP --site-index 70

# Configuration management
fvs-simulate convert-config --output-dir ./cfg/toml
fvs-simulate validate-config
```

## Architecture Overview

### Core Simulation Flow
1. **Tree** objects contain individual tree attributes and growth methods
2. **Stand** objects manage collections of trees and orchestrate simulations
3. **Growth models** are modular components implementing specific equations
4. **Configuration** system uses YAML/JSON files for species parameters and model coefficients

### Key Module Relationships
- `main.py` → Entry point, coordinates simulation components
- `tree.py` → Individual tree growth logic, calls growth model modules
- `stand.py` → Stand-level management, aggregates tree-level results
- `config_loader.py` → Loads and validates configuration from `/cfg/` directory
- Growth modules (`height_diameter.py`, `crown_ratio.py`, etc.) → Implement specific growth equations

### Configuration System
- Species configurations in `/cfg/species/` define growth parameters for ~80+ species
- Model coefficients stored in JSON files (e.g., `sn_height_diameter_coefficients.json`)
- Configuration can be converted between YAML and TOML formats

### Growth Model Implementation Pattern
Each growth model module typically:
1. Loads coefficients from configuration
2. Implements equation-specific logic
3. Provides a main calculation function used by Tree class
4. Includes validation and error handling

### Testing Strategy
- Unit tests for individual modules in `/tests/`
- Comprehensive integration tests in `test_tree_comprehensive.py`
- Test outputs and plots saved to `/test_output/` for verification
- Use real data/parameters from configuration files in tests

## Development Roadmap

### Phase 1: Critical Bug Fixes (1-2 weeks)
**Priority: HIGH - These issues affect simulation accuracy**

1. **Fix Small Tree Growth Time Step Handling**
   - File: `src/fvs_python/tree.py` (lines 119-150)
   - Issue: Chapman-Richards function assumes 5-year growth, doesn't scale properly for other time steps
   - Fix: Implement proper annual growth calculation and accumulation

2. **Fix Tree Age Tracking in Growth Models**
   - File: `src/fvs_python/tree.py` (lines 75-95)
   - Issue: Age is incremented before growth calculations, causing inconsistencies
   - Fix: Store original age, apply growth, then increment age

3. **Add Parameter Validation**
   - Files: All growth model files
   - Issue: No bounds checking on inputs (site index, DBH, etc.)
   - Fix: Add validation methods with species-specific bounds from config

4. **Fix Stand Initialization Inconsistency**
   - File: `src/fvs_python/stand.py` (line 24-26)
   - Issue: Constructor accepts trees list but raises error if empty
   - Fix: Either remove error or change signature to require non-empty list

### Phase 2: Code Quality Improvements (2-3 weeks)
**Priority: MEDIUM - Improves maintainability and reliability**

1. **Consolidate Simulation Functions**
   - File: `src/fvs_python/main.py`
   - Issue: Three overlapping simulation functions (run_simulation, simulate_stand_growth, generate_yield_table)
   - Fix: Create single parameterized simulation engine

2. **Implement Comprehensive Error Handling**
   - Add try/except blocks for file I/O operations
   - Create custom exception classes for domain-specific errors
   - Add user-friendly error messages

3. **Move Hardcoded Values to Configuration**
   - Transition zone thresholds (xmin=1.0, xmax=3.0 in tree.py)
   - Mortality parameters in stand.py
   - Plant effect values in growth models

4. **Standardize Configuration Loading**
   - Update crown_ratio.py to use ConfigLoader instead of direct JSON loading
   - Ensure all models use consistent fallback mechanisms

### Phase 3: Testing & Validation (2-3 weeks)
**Priority: HIGH - Ensures model accuracy**

1. **Add Integration Tests**
   - Full simulation pipeline tests
   - Multi-species stand simulations
   - Edge case handling (extreme site indices, densities)

2. **Improve Test Assertions**
   - Current tests have very relaxed bounds
   - Calibrate expected values against FVS documentation
   - Add regression tests with known good outputs

3. **Add Configuration Tests**
   - Test YAML/TOML loading and conversion
   - Validate all species configurations load correctly
   - Test fallback mechanisms

4. **Performance Benchmarks**
   - Establish baseline performance metrics
   - Test with large stands (1000+ trees)

### Phase 4: Feature Enhancements (3-4 weeks)
**Priority: MEDIUM - Adds value for users**

1. **Add Logging System**
   - Implement structured logging throughout
   - Add debug/info/warning/error levels
   - Include simulation progress tracking

2. **Enhance CLI Interface**
   - Add batch simulation capability
   - Implement configuration file input
   - Add progress bars for long simulations

3. **Improve Visualization**
   - Add interactive plots (plotly/bokeh)
   - Create stand visualization maps
   - Add growth comparison tools

4. **Add Data Export Options**
   - Excel export for yield tables
   - JSON output for web integration
   - SQLite database option for large simulations

### Phase 5: Advanced Features (4-6 weeks)
**Priority: LOW - Future enhancements**

1. **Parallel Processing**
   - Implement multiprocessing for stand simulations
   - Parallelize growth calculations for large stands
   - Add GPU support for matrix operations

2. **Web API Development**
   - RESTful API for simulations
   - WebSocket support for real-time updates
   - Docker containerization

3. **Model Extensions**
   - Add thinning operations
   - Implement disease/pest effects
   - Add economic analysis tools

4. **Machine Learning Integration**
   - Growth model calibration from data
   - Uncertainty quantification
   - Sensitivity analysis tools

## Known Issues & Workarounds

### Current Issues
1. **Competition Factor Not Used in Small Tree Model**
   - Location: `tree.py:_grow_small_tree()`
   - Impact: Small trees don't respond to competition
   - Workaround: Competition effects only apply after transition to large tree model

2. **Test Assertions Too Relaxed**
   - Location: `tests/test_stand.py`
   - Impact: Tests pass but may hide calibration issues
   - Workaround: Review test outputs manually in `/test_output/`

3. **Volume Calculations**
   - Location: `tree.py:get_volume()`
   - Impact: May not match FVS exactly
   - Workaround: Verify against NVEL library if available

### Best Practices When Fixing Issues
1. Always run full test suite after changes
2. Update relevant documentation
3. Add tests for any new functionality
4. Verify changes against FVS documentation
5. Update CHANGELOG.md with significant changes