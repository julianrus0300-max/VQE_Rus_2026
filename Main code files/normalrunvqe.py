# ########################
# MOLECULE SPECIFICATION #
# ########################

# Specify the atoms and their coordinates
geometry = [["H", [0, 0, 0]], ["H", [0,0,0.7414]] 

           ]
# Freezes atomic orbitals. Orbitals start from index 0.
# That means [] is no frozen, [0] is core electrons frozen,
# [0,1] is core and the orbital above it frozen, etc.
freeze = []

# Here you specify the basis set which approximates
# the orbitals of an atom or molecule.
basis = "sto-6g"

# Charge of the atom or molecule.
charge = 0

# Verbose is used for outputting errors.
verbose = 1

# Multiplicity is the spin multiplicity according to 2S + 1
multiplicity = 1

# ######################### #
# PRELIMINARY CALCULATIONS  #
# ######################### #
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularROHF

# This driver creates the system of the molecule and has parameters
# such as geometry, basis, charge, verbose, multiplicity, frozen.
driver = ChemistryDriverPySCFMolecularROHF(geometry=geometry, basis=basis, charge=charge, verbose=verbose, multiplicity=multiplicity, frozen=freeze)

# Grabs the hamiltonian, fock space, and fock state from our driver.
chemistry_hamiltonian, fock_space, hartree_fock_state = driver.get_system()

# Grabs the Hartree Fock energy from the driver.
hartree_fock_energy = driver.mf_energy

print('HARTREE FOCK ENERGY: {}\n'.format(hartree_fock_energy))

# Converts the chemistry hamiltonian to fermionic.
fermionic_hamiltonian = chemistry_hamiltonian.to_FermionOperator()

print('FOCK SPACE AND THE HARTREE-FOCK STATE OCCUPATIONS:')
fock_space.print_state(hartree_fock_state)

# ######################### #
# QUBIT MAPPING HAMILTONIAN #
# ######################### #

from inquanto.mappings import QubitMappingJordanWigner

# To perform VQE calculations, we need to map our hamiltonian
# into a quantum one, so we obtain our qubit hamiltonian by
# using JordanWigner mapping on our fermionic hamiltonian.
jw_map = QubitMappingJordanWigner()
qubit_hamiltonian = jw_map.operator_map(fermionic_hamiltonian)


#print('QUBIT HAMILTONIAN:\n{}'.format(qubit_hamiltonian))



# ##################### #
# CREATE A UCCSD ANSATZ #
# ##################### #

from inquanto.ansatzes import FermionSpaceAnsatzUCCSD

# Creates our ansatz UCCSD based on our fock space and state.
ansatz = FermionSpaceAnsatzUCCSD(fock_space, hartree_fock_state)
print('ANSATZ REPORT:')
print(ansatz.generate_report())
print('\n 2-qubit GATES:  {}'.format(ansatz.circuit_resources()['gates_2q']))
#print("\n ANSATZ GENERATION CIRCUIT:")
#ansatz.state_circuit


# ############################### #
# SIMULATOR AND OPTIMIZER DETAILS #
# ############################### #

# install pytket-qiskit using e.g. pip install pytket-qiskit if necessary


from pytket.extensions.qiskit import AerStateBackend
from inquanto.minimizers import MinimizerScipy

# We assign our backend based on state vector calculations.
backend = AerStateBackend()

# We assign our minimizer using a MinimizerScipy method such as L-BFGS-B.
# This minimizer is important as it can drastically change the amount
# of time to converge.
minimizer = MinimizerScipy(method="L-BFGS-B")

# ############ #
# OPTIMIZATION #
# ############ #

from inquanto.express import run_vqe


# Below runs the VQE given arguments such as the ansatz, qubit_hamiltonian,
# backend, gradient, and minimizer. The gradient can also drastically
# change the calculation time.
vqe = run_vqe(ansatz, qubit_hamiltonian, backend=backend, with_gradient=True, minimizer=minimizer)


# We generate a VQE report.
report = vqe.generate_report()

# We print a piece of our report based on its internal dictionary.
# Refer to the documentation.
print('\nVQE ENERGY: {}'.format(report['final_value']))

