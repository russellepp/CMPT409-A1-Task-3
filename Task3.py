# LAST EDIT BY RUSSELL EPP 2021-06-13 1:15 PM
# BASED ON QISKIT DOCUMENTATION FOR QUANTUM TELEPORTATION
# https://qiskit.org/textbook/ch-algorithms/teleportation.html#3.-Simulating-the-Teleportation-Protocol-

# Do the necessary imports
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import IBMQ, Aer, transpile, assemble
from qiskit.visualization import plot_histogram, plot_bloch_multivector
from qiskit.extensions import Initialize
from qiskit_textbook.tools import random_state, array_to_latex
from math import sqrt, cos, sin, acos, asin, radians, degrees
def create_bell_pair(qc, a, b):
    """Creates a bell pair in qc using qubits a & b"""
    qc.h(a) # Put qubit a into state |+>
    qc.cx(a,b) # CNOT with a as control and b as target

def alice_gates(qc, psi, a):
    qc.cx(psi, a)
    qc.h(psi)

def measure_and_send(qc, a, b):
    """Measures qubits a & b and 'sends' the results to Bob"""
    qc.barrier()
    qc.measure(a,0)
    qc.measure(b,1)

# This function takes a QuantumCircuit (qc), integer (qubit)
# and ClassicalRegisters (crz & crx) to decide which gates to apply
def bob_gates(qc, qubit, crz, crx):
    # Here we use c_if to control our gates with a classical
    # bit instead of a qubit
    qc.x(qubit).c_if(crx, 1) # Apply gates if the registers 
    qc.z(qubit).c_if(crz, 1) # are in the state '1'

## SETUP
# Create random 1-qubit state

#message = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' #Message to send
message = 'Hello World' #Message to send
#message = 'abcdefghijklmnopqrstuvwxyz' #Message to send
for i in range(len(message)):
    letter = message[i] #Letter to send
    letterASCII = ord(letter)
    if letterASCII <= 90:
        quadrant = 1
    elif letterASCII <= 180:
        quadrant = 2
    elif letterASCII <= 270:
        quadrant = 3
    elif letterASCII <= 360:
        quadrant = 4
    else:
        print("Warning: Improper Character Sent")
    psi = [cos(radians(letterASCII)),sin(radians(letterASCII))]
    
    iteration = 1
    found = 0
    bit0 = 0
    bit1 = 0
    while found == 0:
        init_gate = Initialize(psi)
        init_gate.label = "init"

        qr = QuantumRegister(3, name="q")   # Protocol uses 3 qubits
        crz = ClassicalRegister(1, name="crz") # and 2 classical registers
        crx = ClassicalRegister(1, name="crx")
        qc = QuantumCircuit(qr, crz, crx)

        #inverse_init_gate = init_gate.gates_to_uncompute()

        ## STEP 0
        # First, let's initialize Alice's q0
        qc.append(init_gate, [0])
        qc.barrier()

        ## STEP 1
        # Now begins the teleportation protocol
        create_bell_pair(qc, 1, 2)
        qc.barrier()

        ## STEP 2
        # Send q1 to Alice and q2 to Bob
        alice_gates(qc, 0, 1)

        ## STEP 3
        # Alice then sends her classical bits to Bob
        measure_and_send(qc, 0, 1)

        ## STEP 4
        # Bob decodes qubits
        bob_gates(qc, 2, crz, crx)

        ## STEP 5
        # reverse the initialization process
        #qc.append(inverse_init_gate, [2])

        # Need to add a new ClassicalRegister
        # to see the result
        cr_result = ClassicalRegister(1)
        qc.add_register(cr_result)
        qc.measure(2,2)



        # And view the circuit so far:
        #print(qc)
        #print("init: ",psi)

        qasm_sim = Aer.get_backend('qasm_simulator')
        t_qc = transpile(qc, qasm_sim)
        qobj = assemble(t_qc)
        counts = qasm_sim.run(qobj).result().get_counts()
        #print(counts)
        try:
            bit0 += int(counts['0 0 0'])
        except:
            pass
        try:
            bit0 += int(counts['0 0 1'])
        except:
            pass
        try:
            bit0 += int(counts['0 1 0'])
        except:
            pass
        try:
            bit0 += int(counts['0 1 1'])
        except:
            pass
        try:
            bit1 += int(counts['1 0 0'])
        except:
            pass
        try:
            bit1 += int(counts['1 0 1'])
        except:
            pass
        try:
            bit1 += int(counts['1 1 0'])
        except:
            pass
        try:
            bit1 += int(counts['1 1 1'])
        except:
            pass
        if iteration == 100:
            break
        iteration += 1
    outcome = round(degrees(acos(sqrt(bit0/(bit0+bit1)))))
    if quadrant == 1:
        pass
    elif quadrant == 2:
        outcome = 180 - outcome
    elif quadrant == 3:
        outcome = 180 + outcome
    elif quadrant == 4:
        outcome = 360 - outcome
    print(chr(outcome), end='')
print('')

