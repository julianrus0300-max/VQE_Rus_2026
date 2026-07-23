# ########################
# MOLECULE SPECIFICATION #
# ########################


geometry = [["H", [0, 0, 0]], ["H", [0,0,0.7414]] 

           ]

#freeze = [0]
basis = "6-31g"
charge = 0
verbose = 1
multiplicity = 1

# ######################### #
# PRELIMINARY CALCULATIONS  #
# ######################### #
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularROHF


driver = ChemistryDriverPySCFMolecularROHF(geometry=geometry, basis=basis, charge=charge, verbose=verbose, multiplicity=multiplicity)#, frozen=freeze)

chemistry_hamiltonian, fock_space, hartree_fock_state = driver.get_system()
hartree_fock_energy = driver.mf_energy

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

vqe = run_vqe(ansatz, qubit_hamiltonian, backend=backend, with_gradient=True, minimizer=minimizer)

report = vqe.generate_report()

print('\nVQE ENERGY: {}'.format(report['final_value']))


#print('\nVQE REPORT: ')
#vqe.generate_report()