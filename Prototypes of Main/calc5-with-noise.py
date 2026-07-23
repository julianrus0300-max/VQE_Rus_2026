# ########################
# MOLECULE SPECIFICATION #
# ########################
#import sys
#print(sys.executable)

import numpy
from inquanto.protocols import SparseStatevectorProtocol
geometry = [["H", [0,0,0]], ["H", [0,0,0.7414]]]
#geometry = [["H", [0,0,0]]]
#freeze = []
freeze = [3]
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

#Start____
# everything within this start and end probably doesn't work or matter.
from pytket.extensions.qiskit import AerBackend
from qiskit_aer.noise import NoiseModel, depolarizing_error

noise_model = NoiseModel()

error_1q = depolarizing_error(0.001,1)
noise_model.add_all_qubit_quantum_error(error_1q, ['u1', 'u2', 'u3', 'cx'])
error_2q = depolarizing_error(0.01,2)
noise_model.add_all_qubit_quantum_error(error_2q,['cx'])
noisy_backend = AerBackend(noise_model=noise_model)

#end____

from qnexus.client import projects

# Below for local
backend = AerStateBackend()
# Below for h2-1sc
#backend = QuantinuumConfig(device_name="H2-1SC")

minimizer = MinimizerScipy(method="L-BFGS-B")

# Below for h2-1sc
#project_ref = projects.get_or_create(name="Testing1", description="", properties={})

from inquanto.computables import ExpectationValue
from inquanto.algorithms import AlgorithmVQE
from inquanto.protocols import PauliAveraging
objective_expression = ExpectationValue(ansatz, qubit_hamiltonian)
# Below for h2-1sc
#protocol_objective = SparseStatevectorProtocol(backend, project_ref=project_ref)
# Below for local
#protocol_objective = SparseStatevectorProtocol(backend)
protocol_objective = PauliAveraging(backend)

myvqe = AlgorithmVQE(objective_expression=objective_expression, minimizer=minimizer)
myvqe.build(protocol_objective=protocol_objective)


myvqe.run()
print(myvqe.final_value)