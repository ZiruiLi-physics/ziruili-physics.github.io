---
description: Exact diagonalization and DMRG time evolution for the PXP model, with dependencies and usage.
---

# Code &amp; tools

Scripts I use. They are not packages and have not been fully tested; read the source before adapting them.

The PXP model is a common effective model for Rydberg atom arrays:

\[
    H = \sum_i P_{i-1} X_i P_{i+1}, \qquad P = |0\rangle\langle 0|
\]

The two scripts below study its dynamics with exact diagonalization and tensor networks, respectively.

<div class="zl-code-card">
<h3>ed_PXP.py — exact diagonalization</h3>

<dl class="zl-code-meta">
  <dt>Purpose</dt><dd>Builds the PXP Hamiltonian with QuSpin and a custom numba basis, then computes dynamics and observables for small systems.</dd>
  <dt>Requires</dt><dd>Python 3, QuSpin, numba, numpy, scipy, matplotlib</dd>
  <dt>Size</dt><dd>Default <code>N = 16</code>; adjust according to memory and time.</dd>
  <dt>Run</dt><dd><code>python ed_PXP.py</code>; outputs and figures are configured at the end of the script.</dd>
</dl>

```python
from quspin.operators import hamiltonian, exp_op
from quspin.basis import spin_basis_1d
from quspin.basis.user import user_basis
from numba import cfunc, carray
```

<div class="zl-code-actions">
  <a class="zl-btn" href="/notes/downloads/ed_PXP.py">Download ed_PXP.py</a>
</div>
</div>

<div class="zl-code-card">
<h3>PXP_tvdp.py — DMRG / time evolution</h3>

<dl class="zl-code-meta">
  <dt>Purpose</dt><dd>Uses TeNPy MPS for iTEBD and TDVP time evolution, tracking entanglement entropy, correlations and truncation error.</dd>
  <dt>Requires</dt><dd>Python 3, TeNPy, numpy, scipy, matplotlib</dd>
  <dt>Parameters</dt><dd>Defaults: <code>chi_max = 400</code>, <code>dt = 0.1</code>, fourth-order splitting.</dd>
  <dt>Run</dt><dd><code>python PXP_tvdp.py</code>; check convergence in <code>chi_max</code> yourself.</dd>
</dl>

```python
from tenpy.algorithms import tebd, tdvp
from tenpy.networks.mps import MPS
from tenpy.models.pxp import PXPChain
```

<div class="zl-code-actions">
  <a class="zl-btn" href="/notes/downloads/PXP_tvdp.py">Download PXP_tvdp.py</a>
</div>
</div>

!!! warning "On reproducibility"
    The parameters are the ones I used for a project; they are not necessarily right for you. If you hit an <code>omp</code> error, look at the thread settings at the top of <code>ed_PXP.py</code>.
