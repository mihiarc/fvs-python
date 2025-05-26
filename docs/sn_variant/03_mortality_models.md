# Southern Variant - Mortality Models

## Overview
The SN variant uses an SDI-based mortality model comprised of two steps: 1) determining the amount of stand mortality and 2) dispersing stand mortality to individual tree records.

## Background Mortality Model

### Equation 5.0.1 - Individual Tree Background Mortality Rate
```
RI = exp(p0 + p1 * DBH)
```

### Equation 5.0.2 - Cycle Length Adjustment
```
RIP = 1 - (1 - RI)^(Y/10)
```

Where:
- **RI** = proportion of the tree record attributed to mortality
- **RIP** = final mortality rate adjusted to the length of the cycle
- **DBH** = tree diameter at breast height
- **Y** = length of the current projection cycle in years
- **p0, p1** = species-specific coefficients (see Table 5.0.1)

## Table 5.0.1 - Background Mortality Coefficients by Species

### Softwood Species
- **FR (Fraser Fir)**: p0 = 5.1676998, p1 = -0.0077681
- **JU (Eastern Juniper)**: p0 = 9.6942997, p1 = -0.0127328
- **PI (Pine Species)**: p0 = 5.1676998, p1 = -0.0077681
- **PU (Pond Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **SP (Slash Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **SA (Sand Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **SR (Spruce Pine)**: p0 = 5.1676998, p1 = -0.0077681
- **LL (Longleaf Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **TM (Tamarack)**: p0 = 5.5876999, p1 = -0.0053480
- **PP (Pond Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **PD (Pitch Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **WP (White Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **LP (Loblolly Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **VP (Virginia Pine)**: p0 = 5.5876999, p1 = -0.0053480
- **BY (Bald Cypress)**: p0 = 5.5876999, p1 = -0.0053480

### Hardwood Species
- **MG (Magnolia)**: p0 = 5.1676998, p1 = -0.0077681
- **CT (Cottonwood)**: p0 = 5.9617000, p1 = -0.0340128
- **MS (Maple Species)**: p0 = 5.1676998, p1 = -0.0077681
- **MV (Maple Species)**: p0 = 5.9617000, p1 = -0.0340128
- **ML (Maple Species)**: p0 = 5.1676998, p1 = -0.0077681
- **AP (American Persimmon)**: p0 = 5.9617000, p1 = -0.0340128
- **MB (Mountain Birch)**: p0 = 5.1676998, p1 = -0.0077681
- **WT (Water Tupelo)**: p0 = 5.9617000, p1 = -0.0340128
- **BG (Black Gum)**: p0 = 5.1676998, p1 = -0.0077681
- **TS (Tulip Tree)**: p0 = 5.9617000, p1 = -0.0340128
- **HH (Hornbeam)**: p0 = 5.1676998, p1 = -0.0077681
- **SD (Serviceberry)**: p0 = 5.1676998, p1 = -0.0077681
- **RA (Red Ash)**: p0 = 5.1676998, p1 = -0.0077681
- **SY (Sycamore)**: p0 = 5.9617000, p1 = -0.0340128
- **CW (Cottonwood)**: p0 = 5.9617000, p1 = -0.0340128

### Additional Species Groups
- **HM (Eastern Hemlock)**: p0 = 5.1676998, p1 = -0.0077681
- **FM (Flowering Dogwood)**: p0 = 5.1676998, p1 = -0.0077681
- **BE (American Beech)**: p0 = 5.1676998, p1 = -0.0077681
- **RM (Red Maple)**: p0 = 5.1676998, p1 = -0.0077681
- **SV (Silver Maple)**: p0 = 5.1676998, p1 = -0.0077681
- **SM (Sugar Maple)**: p0 = 5.1676998, p1 = -0.0077681
- **BU (Buckeye)**: p0 = 5.1676998, p1 = -0.0077681
- **BB (Basswood)**: p0 = 5.9617000, p1 = -0.0340128
- **SB (Sweet Birch)**: p0 = 5.1676998, p1 = -0.0077681
- **AH (American Hornbeam)**: p0 = 5.1676998, p1 = -0.0077681
- **HI (Hickory)**: p0 = 5.9617000, p1 = -0.0340128
- **CA (American Chestnut)**: p0 = 5.9617000, p1 = -0.0340128
- **HB (Hornbeam)**: p0 = 5.9617000, p1 = -0.0340128

### Oak Species
- **BC (Black Cherry)**: p0 = 5.9617000, p1 = -0.0340128
- **WO (White Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **SO (Southern Red Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **SK (Swamp Chestnut Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **CB (Cucumber Tree)**: p0 = 5.9617000, p1 = -0.0340128
- **TO (Tulip Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **LK (Live Oak)**: p0 = 5.1676998, p1 = -0.0077681
- **OV (Overcup Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **BJ (Black Jack Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **SN (Southern Red Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **CK (Cherrybark Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **WK (Water Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **CO (Chestnut Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **RO (Red Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **QS (Post Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **PO (Pin Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **BO (Black Oak)**: p0 = 5.9617000, p1 = -0.0340128
- **LO (Laurel Oak)**: p0 = 5.9617000, p1 = -0.0340128

### Other Species
- **BK (Black Oak)**: p0 = 5.1676998, p1 = -0.0077681
- **WI (Willow)**: p0 = 5.1676998, p1 = -0.0077681
- **SS (Sweetgum)**: p0 = 5.1676998, p1 = -0.0077681
- **BD (Basswood)**: p0 = 5.1676998, p1 = -0.0077681
- **EL (Elm)**: p0 = 5.1676998, p1 = -0.0077681
- **WE (White Elm)**: p0 = 5.1676998, p1 = -0.0077681
- **AE (American Elm)**: p0 = 5.1676998, p1 = -0.0077681
- **RL (Red Elm)**: p0 = 5.1676998, p1 = -0.0077681
- **OS (Other Softwoods)**: p0 = 5.5876999, p1 = -0.0053480
- **OH (Other Hardwoods)**: p0 = 5.9617000, p1 = -0.0340128
- **OT (Other Trees)**: p0 = 5.9617000, p1 = -0.0340128

## Density-Dependent Mortality

When stand density-related mortality is in effect, the total amount of stand mortality is determined based on the trajectory developed from the relationship between stand SDI and the maximum SDI for the stand.

### Mortality Threshold
- **Default threshold**: 55% of maximum SDI
- **Below threshold**: Use summation of individual tree background mortality rates
- **Above threshold**: Use stand-level density-related mortality rates

## Mortality Dispersion Model

Once the amount of stand mortality is determined, mortality is dispersed to individual tree records based on tree height relative to average stand height.

### Equation 5.0.3 - Mortality Rate by Tree Percentile
```
MR = 0.84525 - (0.01074 * PCTi) + (0.0000002 * PCTi^3)
```

### Equation 5.0.4 - Final Mortality Rate
```
MORT = MR * MWT * 0.1
```

Where:
- **MR** = proportion of tree record attributed to mortality (bounded: 0.01 < MR < 1)
- **PCTi** = tree percentile in the distribution of stand basal area
- **MORT** = final mortality rate of the tree record
- **MWT** = mortality weight value (see Table 5.0.2)

## Table 5.0.2 - Mortality Weight Values by Species

### Softwood Species
- **FR (Fraser Fir)**: MWT = 0.1
- **JU (Eastern Juniper)**: MWT = 0.7
- **PI (Pine Species)**: MWT = 0.3
- **PU (Pond Pine)**: MWT = 0.7
- **SP (Slash Pine)**: MWT = 0.7
- **SA (Sand Pine)**: MWT = 0.7
- **SR (Spruce Pine)**: MWT = 0.1
- **LL (Longleaf Pine)**: MWT = 0.7
- **TM (Tamarack)**: MWT = 0.7
- **PP (Pond Pine)**: MWT = 0.7
- **PD (Pitch Pine)**: MWT = 0.7
- **WP (White Pine)**: MWT = 0.5
- **LP (Loblolly Pine)**: MWT = 0.7
- **VP (Virginia Pine)**: MWT = 0.7
- **BY (Bald Cypress)**: MWT = 0.5
- **PC (Pond Cypress)**: MWT = 0.5
- **HM (Eastern Hemlock)**: MWT = 0.1

### Hardwood Species
- **FM (Flowering Dogwood)**: MWT = 0.3
- **BE (American Beech)**: MWT = 0.3
- **RM (Red Maple)**: MWT = 0.3
- **SV (Silver Maple)**: MWT = 0.3
- **SM (Sugar Maple)**: MWT = 0.1
- **BU (Buckeye)**: MWT = 0.3
- **BB (Basswood)**: MWT = 0.7
- **SB (Sweet Birch)**: MWT = 0.7
- **AH (American Hornbeam)**: MWT = 0.1
- **HI (Hickory)**: MWT = 0.5
- **CA (American Chestnut)**: MWT = 0.7
- **HB (Hornbeam)**: MWT = 0.5

### Oak Species
- **BC (Black Cherry)**: MWT = 0.7
- **WO (White Oak)**: MWT = 0.5
- **SO (Southern Red Oak)**: MWT = 0.9
- **SK (Swamp Chestnut Oak)**: MWT = 0.5
- **CB (Cucumber Tree)**: MWT = 0.7
- **TO (Tulip Oak)**: MWT = 0.7
- **LK (Live Oak)**: MWT = 0.3
- **OV (Overcup Oak)**: MWT = 0.5
- **BJ (Black Jack Oak)**: MWT = 0.7
- **SN (Southern Red Oak)**: MWT = 0.7
- **CK (Cherrybark Oak)**: MWT = 0.7
- **WK (Water Oak)**: MWT = 0.7
- **CO (Chestnut Oak)**: MWT = 0.5
- **RO (Red Oak)**: MWT = 0.5
- **QS (Post Oak)**: MWT = 0.7
- **PO (Pin Oak)**: MWT = 0.7
- **BO (Black Oak)**: MWT = 0.5
- **LO (Laurel Oak)**: MWT = 0.5

### Other Species
- **BK (Black Oak)**: MWT = 0.9
- **WI (Willow)**: MWT = 0.9
- **SS (Sweetgum)**: MWT = 0.7
- **BD (Basswood)**: MWT = 0.3
- **EL (Elm)**: MWT = 0.5
- **WE (White Elm)**: MWT = 0.3
- **AE (American Elm)**: MWT = 0.5
- **RL (Red Elm)**: MWT = 0.3
- **OS (Other Softwoods)**: MWT = 0.5
- **OH (Other Hardwoods)**: MWT = 0.5
- **OT (Other Trees)**: MWT = 0.5

## Mortality Process

1. **Multiple Passes**: The mortality model makes multiple passes through tree records
2. **Accumulation**: Multiplies trees-per-acre value times final mortality rate (MORT)
3. **Reduction**: Reduces trees-per-acre representation until desired mortality level is reached
4. **Basal Area Check**: If stand exceeds basal area maximum sustainable on site, mortality rates are proportionally adjusted

## Implementation Notes

1. Background mortality is calculated for all trees using species-specific coefficients
2. Density-dependent mortality kicks in when stand density exceeds 55% of maximum SDI
3. Mortality is preferentially applied to smaller, less competitive trees
4. Shade tolerance affects mortality susceptibility through the mortality weight values
5. The compound interest formula adjusts mortality rates to the projection cycle length 