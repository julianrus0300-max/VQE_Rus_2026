# ########################
# MOLECULE SPECIFICATION #
# ########################
import numpy
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
ansatz = FermionSpaceAnsatzUCCSD(fock_space, hartree_fock_state)
print('ANSATZ REPORT:')
print(ansatz.generate_report())
print('\n 2-qubit GATES:  {}'.format(ansatz.circuit_resources()['gates_2q']))
#print("\n ANSATZ GENERATION CIRCUIT:")
#ansatz.state_circuit

from pytket.extensions.qiskit import AerStateBackend
from inquanto.minimizers import MinimizerScipy
from qnexus import QuantinuumConfig
backend = AerStateBackend()
#backend = QuantinuumConfig(device_name="H2-1SC")
minimizer = MinimizerScipy(method="L-BFGS-B")

from inquanto.computables import ExpectationValue
from inquanto.algorithms import AlgorithmVQE
expectation_value = ExpectationValue(ansatz, qubit_hamiltonian)

test_vqe = AlgorithmVQE(objective_expression=expectation_value,minimizer=minimizer)
#,initial_parameters=ansatz.state_symbols.construct_random(seed=0))

from inquanto.protocols import PauliAveraging
from pytket.partition import PauliPartitionStrat

#for noise:
#p = ansatz.state_symbols.construct_zeros()
#noisy_protocol = PauliAveraging(backend=backend, shots_per_circuit=1000,pauli_partition_strategy=PauliPartitionStrat.CommutingSets)
#noisy_protocol.build(p,ansatz, qubit_hamiltonian)
# Above is something along the lines of what protocol_objective should be replaced with.
#test_vqe.build(protocol_objective=noisy_protocol)
test_vqe.build(protocol_objective=SparseStatevectorProtocol(AerStateBackend()))

# Below actually runs the vqe and prints the final vqe energy.
test_vqe.run()
print(test_vqe.final_value)