# Note: Refer to the comments for normalrunvqe.py for all
# of the already mentioned steps before expectation value
# and initial parameters.




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
#from pytket import Circuit, OpType
ansatz = FermionSpaceAnsatzUCCSD(fock_space, hartree_fock_state, QubitMappingJordanWigner())
print('ANSATZ REPORT:')
print(ansatz.generate_report())
print('\n 2-qubit GATES:  {}'.format(ansatz.circuit_resources()['gates_2q']))
#print("\n ANSATZ GENERATION CIRCUIT:")
#ansatz.state_circuit

from pytket.extensions.qiskit import AerBackend
from inquanto.minimizers import MinimizerScipy
from qnexus import QuantinuumConfig

from qnexus.client import projects

# Below for local
backend = AerBackend()
# Below for h2-1sc
#backend = QuantinuumConfig(device_name="H2-1SC")

minimizer = MinimizerScipy(method="L-BFGS-B")

# Below for h2-1sc
#project_ref = projects.get_or_create(name="Testing1", description="", properties={})

from inquanto.computables import ExpectationValue, ExpectationValueDerivative
from inquanto.algorithms import AlgorithmVQE
from inquanto.protocols import PauliAveraging

# Initializes the ansatz circuit parameters to zero to define
# the starting state. This establishes the baseline quantum state
# before the VQE optimization loop begins updating the parameters.
initial_parameters = ansatz.state_symbols.construct_zeros()

# Configures the basic ExpectationValue protocol to measure the operator's
# properties on the state. Unlike derivative methods, this directly prepares
# the routine for calculating the standard expected value of the observable.
objective_expression = ExpectationValue(ansatz, qubit_hamiltonian)

# Gather symbols AFTER constructing initial parameters
free_symbols = ansatz.free_symbols_ordered() 

# Defines the target objective function using the PauliAveraging protocol.
# This will calculate the system's energy expectation values by averaging
# measurements over the necessary Pauli strings.
protocol_objective = PauliAveraging(backend, shots_per_circuit=4096)

# This generates the architecture-dependent measurement circuits required
# for the objective function. It maps the system's ansatz state and qubit
# operators into a physical execution plan.
protocol_objective.build(initial_parameters, ansatz, qubit_hamiltonian)

# Constructs the analytical gradent of the objective function using
# parameter derivatives. This tells the optimizer exactly how the
# energy changes with respect to each circuit parameter.
gradient = ExpectationValueDerivative(ansatz,qubit_hamiltonian,free_symbols)

# Only really needed when printing out the circuits.
protocol_objective.compile_circuits(optimization_level=1)


# Instantiates the VQE solver using the AlgorithmVQE class and binds the
# starting parameers. This serves as the main execution engine that will
# iteratively optimize our quantum circuit parameters.
myvqe = AlgorithmVQE(
    minimizer=minimizer, 
    objective_expression=objective_expression, 
    #gradient_expression=gradient,
    initial_parameters=initial_parameters
)

# Couples the VQE algorithm framework with our defined objective and gradient
# protocols. This builds the complete optimization loop, allowing the classical
# optimizer to communicate smoothly with the quantum backend.
myvqe.build(protocol_objective=protocol_objective, protocol_gradient=gradient)

# Runs the calculation
myvqe.run()
print(myvqe.final_value)

#print(protocol_objective.dataframe_measurements())


