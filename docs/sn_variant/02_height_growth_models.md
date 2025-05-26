# Southern Variant - Height Growth Models

## Overview
The Southern Variant uses height growth models to predict tree height increment. This document contains the equations, coefficients, and shade tolerance parameters for height growth calculations.

## Large-Tree Height Growth Model

The SN variant follows the approach of Wensel and others (1987) where potential height growth is calculated for every tree and modified based on individual tree crown ratio and relative height in the stand.

### Equation 4.7.2.1 - Height Growth Calculation
```
HTG = POTHTG * (0.25 * HGMDCR + 0.75 * HGMDRH)
```

Where:
- **HTG** = periodic height growth
- **POTHTG** = potential periodic height growth (see section 4.6.1)
- **HGMDCR** = crown ratio modifier (bounded to HGMDCR < 1.0)
- **HGMDRH** = relative height modifier

### Equation 4.7.2.2 - Crown Ratio Modifier
```
HGMDCR = 100 * CR^3.0 * exp(-5.0*CR)
```

Where:
- **CR** = crown ratio expressed as a proportion
- Uses Hoerl's Special Function (HSF) form with range 0.0 to 1.0
- Parameters chosen to maximize height growth for crown ratios between 45% and 75%

### Relative Height Modifier Equations

The relative height modifying function (HGMDRH) is based on the Generalized Chapman-Richards function and uses the following equations:

#### Equation 4.7.2.3
```
FCTRKX = ((RHK / RHYXS)^(RHM - 1)) - 1
```

#### Equation 4.7.2.4
```
FCTRRB = (-1.0 * RHR) / (1 - RHB)
```

#### Equation 4.7.2.5
```
FCTRXB = RELHT^(1 - RHB) - RHXS^(1 - RHB)
```

#### Equation 4.7.2.6
```
FCTRM = 1 / (1 - RHM)
```

#### Equation 4.7.2.7
```
HGMDRH = RHK * (1 + FCTRKX * exp(FCTRRB * FCTRXB))^FCTRM
```

Where:
- **RELHT** = subject tree's height relative to the 40 tallest trees in the stand
- **RH...** = relative height modifier coefficients based on shade tolerance (see tables below)

## Table 4.7.2.1 - Relative Height Modifier Coefficients by Shade Tolerance

### Very Tolerant Species
- RHR = 20
- RHYXS = 0.20
- RHM = 1.1
- RHB = -1.10
- RHXS = 0
- RHK = 1

### Tolerant Species
- RHR = 16
- RHYXS = 0.15
- RHM = 1.1
- RHB = -1.20
- RHXS = 0
- RHK = 1

### Intermediate Species
- RHR = 15
- RHYXS = 0.10
- RHM = 1.1
- RHB = -1.45
- RHXS = 0
- RHK = 1

### Intolerant Species
- RHR = 13
- RHYXS = 0.05
- RHM = 1.1
- RHB = -1.60
- RHXS = 0
- RHK = 1

### Very Intolerant Species
- RHR = 12
- RHYXS = 0.01
- RHM = 1.1
- RHB = -1.60
- RHXS = 0
- RHK = 1

## Table 4.7.2.2 - Shade Tolerance by Species

### Very Tolerant Species
- FR (Fraser Fir)
- SR (Spruce Pine)
- HM (Eastern Hemlock)
- SM (Sugar Maple)
- AH (American Hornbeam)
- DW (Dogwood)
- PS (Persimmon)
- AB (American Basswood)
- HY (Hickory)

### Tolerant Species
- PI (Pine Species)
- FM (Flowering Dogwood)
- BE (American Beech)
- RM (Red Maple)
- SV (Silver Maple)
- BU (Buckeye)
- MG (Magnolia)
- MS (Maple Species)
- ML (Maple Species)
- MB (Mountain Birch)
- BG (Black Gum)
- HH (Hornbeam)
- SD (Serviceberry)
- RA (Red Ash)
- LK (Live Oak)
- BD (Basswood)
- EL (Elm)
- WE (White Elm)
- AS (Ash Species)
- GA (Green Ash)
- LB (Loblolly Bay)
- HA (Hackberry)

### Intermediate Species
- WP (White Pine)
- BY (Bald Cypress)
- PC (Pond Cypress)
- HI (Hickory)
- CT (Cottonwood)
- MV (Maple Species)
- WO (White Oak)
- SK (Swamp Chestnut Oak)
- OV (Overcup Oak)
- SY (Sycamore)
- CO (Chestnut Oak)
- RO (Red Oak)
- BO (Black Oak)
- LO (Laurel Oak)
- EL (Elm)
- AE (American Elm)
- OS (Other Softwoods)
- OH (Other Hardwoods)
- OT (Other Trees)

### Intolerant Species
- JU (Eastern Juniper)
- PU (Pond Pine)
- SP (Slash Pine)
- SA (Sand Pine)
- LL (Longleaf Pine)
- TM (Tamarack)
- PP (Pond Pine)
- PD (Pitch Pine)
- LP (Loblolly Pine)
- BB (Basswood)
- SB (Sweet Birch)
- BC (Black Cherry)
- CB (Cucumber Tree)
- TO (Tulip Oak)
- BJ (Black Jack Oak)
- SN (Southern Red Oak)
- CK (Cherrybark Oak)
- WK (Water Oak)
- QS (Post Oak)
- PO (Pin Oak)
- SS (Sweetgum)
- CA (American Chestnut)
- WA (Water Ash)
- BA (Black Ash)
- HL (Honey Locust)
- BN (Black Walnut)
- WN (White Walnut)
- SU (Sugar Maple)
- YP (Yellow Poplar)
- AP (American Persimmon)
- WT (Water Tupelo)
- TS (Tulip Tree)

### Very Intolerant Species
- CW (Cottonwood)
- BT (Black Tupelo)
- SO (Southern Red Oak)
- BK (Black Oak)
- WI (Willow)

## Height Growth Characteristics

1. **Crown Ratio Effect**: Height growth is maximized for trees with crown ratios between 45% and 75%
2. **Relative Height Effect**: The modifier decreases with decreasing relative height and species intolerance
3. **Asymptotic Behavior**: Height growth reaches an upper asymptote of 1.0 at:
   - Relative height of 1.0 for intolerant species
   - Relative height of 0.7 for tolerant species
4. **Range**: Both HGMDCR and HGMDRH have ranges between 0.0 and 1.0

## Implementation Notes

1. Potential height growth (POTHTG) is calculated using small-tree height increment model methodology
2. The crown ratio modifier uses Hoerl's Special Function form
3. Relative height is calculated as the subject tree's height relative to the 40 tallest trees in the stand
4. Shade tolerance classifications determine the relative height modifier coefficients
5. The final height growth is a weighted combination of crown ratio (25%) and relative height (75%) effects 