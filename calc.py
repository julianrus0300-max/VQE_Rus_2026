

# ########################
# MOLECULE SPECIFICATION #
# ########################

# basislist below is actually a list of frozen orbitals.
# I refuse to go and replace all the variable names with
# something else so I just renamed frozenlist to basislist.
import sys


if input("Type yes to run:\n") != "yes":
    sys.exit()

#basislist = [[0,8,9,10,11,12,13,14,15,16]]
#basislist = [[0,5,6,7,8,9,10,11,12,13,14,15,16]]
#basislist = [[0]]
#for x in range(5,34,1):
    #basislist[0].append(x)
#basis = "cc-pvdz"
basislist = ["sto-3g",
             "sto-6g",
             "3-21g",
             "6-31g",
             "6-31g(d)",
             "6-31g(d,p)",
             "6-31+g(d,p)",
             "cc-pvdz",
             "def2-svp",
             "def2-tzvp"
             "6-311g(d,p)"
             ]
from pathlib import Path
downloads_path = Path.home() / "Downloads"
file_path = downloads_path / "VQE_outputcc.txt"
energy_path = downloads_path / "VQE_energyonlycc.txt"
qubitgate_path = downloads_path / "VQE_amt2qubitgatecc.txt"
n_parameter_path = downloads_path / "VQE_n_parametercc.txt"
time_path = downloads_path / "VQE_timecc.txt"
basis_path = downloads_path / "VQE_basiscc.txt"
qubit_path = downloads_path / "VQE_qubitcount.txt"

writeorappend = "w"

myfile = open(file_path, writeorappend, encoding="utf-8")
energyonlyfile = open(energy_path, writeorappend, encoding="utf-8")
qubitgatefile = open(qubitgate_path, writeorappend, encoding="utf-8")
n_parameterfile = open(n_parameter_path, writeorappend, encoding="utf-8")
timefile = open(time_path, writeorappend, encoding="utf-8")
basisfile = open(basis_path, writeorappend, encoding="utf-8")
qubitcount = open(qubit_path, writeorappend, encoding="utf-8")

myfile.write("\n START___________________\n")

#for removeorbitalindex in range(5, 34, 1):
#basislist[0].remove(removeorbitalindex)
for mybasis in basislist:
# The for loop here only has the one list inside of basislist.

    geometry = [["H", [0, 0, 0]], ["H", [0, 0, 0.7414]]]

    #freeze = [0,6,7,8]
    #basis = mybasis
    charge = 0
    verbose = 1

    # ######################### #
    # PRELIMINARY CALCULATIONS  #
    # ######################### #
    from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularRHF


    driver = ChemistryDriverPySCFMolecularRHF(geometry=geometry, basis=mybasis, charge=charge, verbose=verbose)

    chemistry_hamiltonian, fock_space, hartree_fock_state = driver.get_system()
    hartree_fock_energy = driver.mf_energy
    #total_orbitals = len(driver._mf.mo_energy)
    #all_indices = list(range(total_orbitals))
    #print(all_indices)
    #sys.exit()
    print('HARTREE FOCK ENERGY: {}\n'.format(hartree_fock_energy))

    fermionic_hamiltonian = chemistry_hamiltonian.to_FermionOperator()

    print('FOCK SPACE AND THE HARTREE-FOCK STATE OCCUPATIONS:')
    fock_space.print_state(hartree_fock_state)

    # ######################### #
    # QUBIT MAPPING HAMILTONIAN #
    # ######################### #

    from inquanto.mappings import QubitMappingJordanWigner

    jw_map = QubitMappingJordanWigner()
    qubit_hamiltonian = jw_map.operator_map(fermionic_hamiltonian)
    #print('QUBIT HAMILTONIAN:\n{}'.format(qubit_hamiltonian))



    # ##################### #
    # CREATE A UCCSD ANSATZ #
    # ##################### #

    from inquanto.ansatzes import FermionSpaceAnsatzUCCSD
    from pytket import Circuit, OpType
    ansatz = FermionSpaceAnsatzUCCSD(fock_space, hartree_fock_state)
    print('ANSATZ REPORT:')
    print(ansatz.generate_report())
    print('\n 2-qubit GATES:  {}'.format(ansatz.circuit_resources()['gates_2q']))
    amt2qubitgate = ansatz.circuit_resources()['gates_2q']
    ansatzreport = ansatz.generate_report()
    

    #print("\n ANSATZ GENERATION CIRCUIT:")
    #ansatz.state_circuit


    # ############################### #
    # SIMULATOR AND OPTIMIZER DETAILS #
    # ############################### #

    # install pytket-qiskit using e.g. pip install pytket-qiskit if necessary


    from pytket.extensions.qiskit import AerStateBackend
    from inquanto.minimizers import MinimizerScipy

    backend = AerStateBackend()
    minimizer = MinimizerScipy(method="L-BFGS-B")

    # ############ #
    # OPTIMIZATION #
    # ############ #

    from inquanto.express import run_vqe
    import time
    start_time = time.time()
    vqe = run_vqe(ansatz, qubit_hamiltonian, backend=backend, with_gradient=True, minimizer=minimizer)
    end_time = time.time()
    report = vqe.generate_report()

    print('\nVQE ENERGY: {}'.format(report['final_value']))


    myfile.write(f"\n Ansatz Report for {mybasis} was: {ansatzreport}")
    myfile.write(f"\n 2-qubit gates for {mybasis} was: {amt2qubitgate}")
    calctime = end_time - start_time
    myfile.write(f"\n Time for {mybasis} was {calctime:.4f}")
    myfile.write(f"\n VQE energy for {mybasis} = {report['final_value']} \n")
    myfile.flush()
    energyonlyfile.write(f"{report['final_value']}\n")
    energyonlyfile.flush()
    qubitgatefile.write(f"{amt2qubitgate}\n")
    qubitgatefile.flush()
    n_parameterfile.write(f"{ansatzreport['n_parameters']}\n")
    n_parameterfile.flush()
    timefile.write(f"{calctime:.4f}\n")
    timefile.flush()
    basisfile.write(f"{mybasis}\n")
    basisfile.flush()
    qubitcount.write(f"{ansatzreport['n_qubits']}\n")
    qubitcount.flush()

#print('\nVQE REPORT: ')
myfile.write("\n END___________________")
myfile.flush()
#vqe.generate_report()