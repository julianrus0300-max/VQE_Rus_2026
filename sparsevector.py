# Note: Refer to normalrunvqe.py for comments related to all the stuff
# done before the ExpectationValue functions.

# ########################
# MOLECULE SPECIFICATION #
# ########################
#import sys
#print(sys.executable)


from inquanto.protocols import SparseStatevectorProtocol
geometry = [["H", [0,0,0]], ["H", [0,0,0.7414]]]
#geometry = [["H", [0,0,0]]]
#freeze = []
freeze = []
multiplicity = 1
basis = "6-31g"
charge = 0
verbose = 1

# ######################### #
# PRELIMINARY CALCULATIONS  #
# ######################### #
from inquanto.extensions.pyscf import ChemistryDriverPySCFMolecularROHF


driver = ChemistryDriverPySCFMolecularROHF(geometry=geometry, basis=basis, charge=charge, verbose=verbose, frozen=freeze, multiplicity=multiplicity)

chemistry_hamiltonian, fock_space, hartree_fock_state = driver.get_system()
hartree_fock_energy = driver.mf_energy
print(driver.mf_energy)
print(len(driver._mf.mo_energy))

#print('HARTREE FOCK ENERGY: {}\n'.format(hartree_fock_energy))

fermionic_hamiltonian = chemistry_hamiltonian.to_FermionOperator()

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
ansatz = FermionSpaceAnsatzUCCSD(fock_space, hartree_fock_state, QubitMappingJordanWigner())
print('ANSATZ REPORT:')
print(ansatz.generate_report())
print('\n 2-qubit GATES:  {}'.format(ansatz.circuit_resources()['gates_2q']))
#print("\n ANSATZ GENERATION CIRCUIT:")
#ansatz.state_circuit

from pytket.extensions.qiskit import AerStateBackend
from inquanto.minimizers import MinimizerScipy
from qnexus import QuantinuumConfig

from qnexus.client import projects

# Below for local
backend = AerStateBackend()
# Below for h2-1sc
#backend = QuantinuumConfig(device_name="H2-1SC")

minimizer = MinimizerScipy(method="L-BFGS-B")

# Below for h2-1sc
#project_ref = projects.get_or_create(name="Testing1", description="", properties={})

from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.algorithms import AlgorithmVQE
from inquanto.protocols import PauliAveraging
objective_expression = ExpectationValue(ansatz, qubit_hamiltonian)
expectationvaluegrad = ExpectationValueDerivative(ansatz, qubit_hamiltonian, ansatz.free_symbols_ordered())
# Below for h2-1sc
#protocol_objective = SparseStatevectorProtocol(backend, project_ref=project_ref)

# Below for local
# Only difference when assigning backends is for protocol_objective,
# you use sparsevectorstateprotocol given the aerstatebackend, no shots.
protocol_objective = SparseStatevectorProtocol(backend)

initial_parameters = ansatz.state_symbols.construct_zeros()


# Only difference here between using pauli vs sparsestate is you use the protocol objective
# for both the objective AND gradient parameters as part of building the vqe.
myvqe = AlgorithmVQE(minimizer=minimizer, objective_expression=objective_expression, gradient_expression=expectationvaluegrad,initial_parameters=initial_parameters)
myvqe.build(protocol_objective=protocol_objective, protocol_gradient=protocol_objective)


myvqe.run()
print(myvqe.final_value)