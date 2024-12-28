def calculate_rsisp(si_site, si_min, si_max):
    """
    Calculate the RSI (relative site index) for a given site species.
    """
    return (si_site - si_min) / (si_max - si_min)

def calculate_mgspix(rsisp, sig_min, sig_max, a, b):
    """
    Calculate the MGSPIX (modified growth site productivity index) transformation index.
    """
    return a + b *(rsisp * (sig_max - sig_min) + sig_min)

def calculate_mgrsi(mgspix, sig_min, sig_max, c, d):
    """
    Calculate the MGRSI (modified growth relative site index) for each site index group.
    """
    return ((c+d * mgspix) - sig_min) / (sig_max - sig_min)

def calculate_sisp(mgrsi, si_min, si_max):
    """
    Calculate the species site index.
    """
    return mgrsi * (si_max - si_min) + si_min


