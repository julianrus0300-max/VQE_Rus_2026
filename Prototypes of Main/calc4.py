import time

def display_top_5_lowest_energies(basis_sets, energies, times):
    """
    Pairs basis sets with their respective energies and compute times,
    sorts them by lowest energy, and prints the top 5.
    """
    # Combine the lists into tuples: (energy, time, basis_set)
    combined_data = list(zip(energies, times, basis_sets))
    
    # Sort primarily by energy (ascending order = lowest energy first)
    sorted_data = sorted(combined_data, key=lambda x: x[0])
    
    # Take the top 5 lowest energies
    top_5 = sorted_data[:15]
    
    # Print the results nicely
    print(f"{'Rank':<5} | {'Basis Set':<15} | {'Energy (Hartree)':<18} | {'Time (s)':<10}")
    print("-" * 56)
    for rank, (energy, time, basis) in enumerate(top_5, 1):
        print(f"{rank:<5} | {basis:<15} | {energy:<18.6f} | {time:<10.2f}")

basislist = [
    # --- Pople Basis Sets (Great for quick HF / DFT) ---
    "sto-3g",
    "sto-6g",
    "3-21g",       # Minimal basis: ultra-fast, purely qualitative
    "6-31g",        # Split-valence: decent for fast geometry optimization
    "6-31g(d)",     # Polarized: adds d-functions to C (essential for bonds)
    "6-31g(d,p)",   # Polarized: adds p-functions to H as well
    "6-31+g(d,p)",  # Diffuse & Polarized: good if evaluating anions/excited states
    "6-311g(d,p)",
      # Triple-zeta Pople: solid accuracy for DFT energy
    
    # --- Dunning's Correlation-Consistent Sets (Best for MP2, CCSD, CBS extrapolation) ---
    "cc-pVDZ",      # Double-zeta: good starting point for correlated methods
    "cc-pVTZ",      # Triple-zeta: excellent balance of speed and high accuracy
    "cc-pVQZ",      # Quadruple-zeta: approach chemical accuracy (heavy computation)
    "aug-cc-pVTZ",  # Augmented with diffuse functions: overkill for neutral CH4, but ultra-accurate
    
    # --- Karlsruhe (Ahlrichs) Def2 Sets (Modern, efficient alternatives to Pople) ---
    "def2-SVP",     # Split-valence polarized: comparable to 6-31G(d) but better optimized
    "def2-TZVP",    # Triple-zeta valence polarized: highly recommended for accurate DFT
    "def2-QZVP"     # Quadruple-zeta valence polarized: extremely high precision
]


energylist = []
timelist = []

#basislist = ["sto-3g", "sto-6g", "3-21g", "6-31g"]
for mybasis in basislist:

    geometry = [["H", [0, 0, 0]], ["H", [0,0,0.7414]]]
    
    #freeze = [0]
    basis = mybasis
    charge = 0
    verbose = 1
    multiplicity = 1
    start = time.time()
    from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularROHF
    driver = ChemistryDriverPySCFMolecularROHF(geometry=geometry, basis=basis, charge=charge, verbose=verbose, multiplicity=multiplicity)
    chemistry_hamiltonian, fock_space, hartree_fock_state = driver.get_system()
    try:
        print(2*len(driver._mf.mo_energy))
    except:
        print("Unlucky")
    end = time.time()
    timelist.append(end - start)
    energylist.append(driver.mf_energy)


display_top_5_lowest_energies(basislist, energylist, timelist)