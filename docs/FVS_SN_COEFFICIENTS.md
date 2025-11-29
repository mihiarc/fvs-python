# FVS Southern Variant (SN) Official Coefficients

**Source:** USDA Forest Service ForestVegetationSimulator Repository
**URL:** https://github.com/USDAForestService/ForestVegetationSimulator
**Extracted:** 2025-11-29

This document contains the official FVS-SN coefficients for the four southern yellow pine species used in FVS-Python.

## Species Codes and Indices

| Common Name | FVS Code | Array Index |
|-------------|----------|-------------|
| Shortleaf Pine | SP | 5 |
| Slash Pine | SA | 6 |
| Longleaf Pine | LL | 8 |
| Loblolly Pine | LP | 13 |

---

## 1. Height-Diameter Relationships (Curtis-Arney)

**Source file:** `sn/htdbh.f`

### Equation

For DBH >= 3.0 inches:
```
H = 4.5 + P2 * exp(-P3 * DBH^P4)
```

For DBH < 3.0 inches (linear interpolation):
```
H = ((4.5 + P2*exp(-P3*3^P4) - 4.51) * (DBH - DB) / (3 - DB)) + 4.51
```

Where:
- `H` = Total tree height (feet)
- `DBH` = Diameter at breast height (inches)
- `DB` = Budwidth transition diameter (inches)

### Coefficients

| Species | P2 | P3 | P4 | DB (budwidth) |
|---------|-----|-----|-----|---------------|
| SP (5) | 444.0921666 | 4.11876312 | -0.30617043 | 0.5 |
| SA (6) | 1087.101439 | 5.10450596 | -0.24284896 | 0.5 |
| LL (8) | 98.56082813 | 3.89930709 | -0.86730393 | 0.5 |
| LP (13) | 243.860648 | 4.28460566 | -0.47130185 | 0.5 |

### Fort Bragg Forest (IFOR=20) Override Coefficients

| Species | P2 | P3 | P4 |
|---------|-----|-----|-----|
| SA (6) | 110.3 | 7.0670 | -1.0420 |
| LL (8) | 114.6 | 4.1840 | -0.6940 |
| LP (13) | 184.3 | 4.2660 | -0.5496 |

---

## 2. Large Tree Diameter Growth

**Source file:** `sn/dgf.f`

### Equation

```
ln(DDS) = CONSPP + INTERC + LDBH*ln(D) + DBH2*D^2 + LCRWN*ln(CR)
          + HREL*RELHT + PLTB*BA + PNTBL*PBAL
          + [forest type terms] + [ecological unit terms]
```

Where:
- `DDS` = Change in squared diameter (inside bark)
- `D` = DBH (inches)
- `CR` = Crown ratio (percent)
- `RELHT` = Relative height (HT/AVH, capped at 1.5)
- `BA` = Stand basal area (sq ft/acre)
- `PBAL` = Point basal area of larger trees

### Core Coefficients

| Species | INTERC | LDBH | DBH2 | LCRWN |
|---------|--------|------|------|-------|
| SP (5) | -0.008942 | 1.238170 | -0.001170 | 0.053076 |
| SA (6) | -1.641698 | 1.461093 | -0.002530 | 0.265872 |
| LL (8) | -1.331052 | 1.098112 | -0.001834 | 0.184512 |
| LP (13) | 0.222214 | 1.163040 | -0.000863 | 0.028483 |

### Competition & Site Coefficients

| Species | HREL | PLTB | PNTBL | ISIO (SI coef) |
|---------|------|------|-------|----------------|
| SP (5) | 0.040334 | -0.004394 | -0.003271 | 0.004723 |
| SA (6) | 0.069104 | -0.002939 | -0.004873 | 0.006851 |
| LL (8) | 0.388018 | -0.002182 | -0.002898 | 0.008774 |
| LP (13) | 0.006935 | -0.003408 | -0.004184 | 0.005018 |

### Slope/Aspect Coefficients

| Species | TANS (slope) | FCOS (cos aspect) | FSIN (sin aspect) |
|---------|--------------|-------------------|-------------------|
| SP (5) | -0.704687 | 0.127667 | 0.028391 |
| SA (6) | -0.018479 | -0.193157 | -0.251016 |
| LL (8) | 0.225213 | 0.086883 | 0.107445 |
| LP (13) | -0.759347 | 0.185360 | -0.072842 |

### Fort Bragg Special Equations (IFOR=20)

For Longleaf (LL, species 8):
```
DG5 = (D*BARK) * ((-0.4553*(0.09737-exp(-0.2428*D)))
      + 0.05574*(CR/100) - 0.0002965*BA
      - 0.00002481*PBA - 0.001192*((PCT/100)^(-0.9663))
      + 0.0010110*SI - 0.007711*RELHT)
```

For Loblolly (LP, species 13):
```
DG5 = (D*BARK) * ((-0.3428*(-0.1741-exp(-0.1328*D)))
      + 0.1145*(CR/100) - 0.0001682*BA
      - 0.00003978*PBA - 0.159400*((PCT/100)^(-0.1299))
      + 0.0006204*SI + 0.02474*RELHT)
```

---

## 3. Crown Ratio Model

**Source file:** `sn/crown.f`

### Mean Crown Ratio (MCR) Equations

The SN variant uses 5 different equation types depending on species:

**Type 1 - Hoerl's Equation:**
```
ACR = exp(a + b*ln(RELSDI) + c*RELSDI)
```

**Type 2 - Power Equation:**
```
ACR = exp(a + b*ln(RELSDI))
```

**Type 3 - Linear Equation:**
```
ACR = a + c*RELSDI
```

**Type 4 - Logarithmic Equation:**
```
ACR = a + b*log10(RELSDI)
```

**Type 5 - Inverse/Hyperbolic Equation:**
```
ACR = RELSDI / (a*RELSDI + b)
```

Where `RELSDI = (SDIAC / SDIDEF) * 10`, bounded 1.0 to 12.0

### MCR Coefficients (MCREQN array)

| Species | Eq Type | a | c | b | b(log) | b(inv) |
|---------|---------|---|---|---|--------|--------|
| SP (5) | 4 (Log) | 47.7297 | 0.0 | 0.0 | -16.352 | 0.0 |
| SA (6) | 4 (Log) | 42.8255 | 0.0 | 0.0 | -15.0135 | 0.0 |
| LL (8) | 4 (Log) | 42.84 | 0.0 | 0.0 | -5.62 | 0.0 |
| LP (13) | 1 (Hoerl) | 3.8284 | 0.0172 | -0.2234 | 0.0 | 0.0 |

### Weibull Distribution for Individual Tree Crown Ratio

```
CR = A + B * (-ln(1-X))^(1/C)
```

Where:
- `X` = Tree's position in basal area distribution (0.05 to 0.95)
- `B = B0 + B1 * MCR`

### Weibull Coefficients

| Species | A | B0 | B1 | C |
|---------|---|----|----|---|
| SP (5) | 4.6721 | -3.9456 | 1.0509 | 3.0228 |
| SA (6) | 3.8940 | -4.7342 | 0.9786 | 2.9082 |
| LL (8) | 3.9771 | 14.3941 | 0.5189 | 3.7531 |
| LP (13) | 4.9701 | -14.6680 | 1.3196 | 2.8517 |

---

## 4. Mortality Model

**Source file:** `sn/morts.f`

### Background Mortality Rate

```
RI = 1 / (1 + exp(B0 + B1*D))
```

Where:
- `RI` = Annual background mortality probability
- `D` = DBH (inches)

### Background Mortality Coefficients

| Species | PMSC (B0) | PMD (B1) |
|---------|-----------|----------|
| SP (5) | 5.5876999 | -0.0053480 |
| SA (6) | 5.5876999 | -0.0053480 |
| LL (8) | 5.5876999 | -0.0053480 |
| LP (13) | 5.5876999 | -0.0053480 |

### SDI-Based Mortality (Competition)

```
T = CONST * D^(-1.605)
```

Where `CONST = SDIMAX / 0.02483133`

Mortality thresholds:
- Lower limit (PMSDIL): 55% of max SDI
- Upper limit (PMSDIU): 85% of max SDI

When stand density exceeds PMSDIL:
```
RN = 1 - (1 - ((T - TN10) / T))^(1/FINT)
```

Applied mortality rate (`RIP`):
- `RIP = RN` when density > 55% max SDI
- `RIP = RI` when density <= 55% max SDI

### Tree-Level Mortality Calculation

```
WKI = P * (1 - (1 - RIP)^FINT) * X
```

Where:
- `P` = Trees per acre represented
- `FINT` = Cycle length (years)
- `X` = Mortality multiplier (from MORTMULT keyword)

---

## 5. Site Index Reference

All site index values should use the curves from **Carmean and others (1989)**.

Base ages:
- Most southern pines: Base age 50
- Use dominant/codominant trees for site index estimation

---

## Notes for FVS-Python Implementation

1. **Species array indexing**: FVS uses 1-based Fortran arrays. Convert to 0-based Python indexing.

2. **Fort Bragg overrides**: Consider making forest-specific coefficients configurable.

3. **Transition zone**: Small-to-large tree transition uses DBH range 1.0 to 3.0 inches with weighted blending.

4. **Units**: All equations use:
   - DBH in inches
   - Height in feet
   - Basal area in sq ft/acre
   - Site index in feet (base age 50)

5. **Crown ratio**: Stored as percentage (0-100) in some places, proportion (0-1) in others.

6. **Time step**: Default growth period is 5 years. Scale appropriately for other time steps.
