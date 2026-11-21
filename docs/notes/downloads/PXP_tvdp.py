import numpy as np
import scipy
import matplotlib.pyplot as plt
import matplotlib
np.set_printoptions(precision=5, suppress=True, linewidth=100)
plt.rcParams['figure.dpi'] = 150

import tenpy
import tenpy.linalg.np_conserved as npc
from tenpy.algorithms import tebd, tdvp
from tenpy.networks.mps import MPS
from tenpy.models.pxp import PXPChain
# from user_models import PXPChain

def iTEBD(psi, model, name):

    model.H_bonds = model.calc_H_bond_from_MPO()
    tebd_params = {
        'N_steps': 1,
        'dt': 0.1,
        'order': 4,
        'trunc_params': {
            'chi_max': 400,
            'svd_min': 1.e-12
        }
    }
    eng = tebd.TEBDEngine(psi, model, tebd_params)

    def measurement(eng, data):
        keys = ['t', 'entropy', 'corr_Z', 'trunc_err']
        if data is None:
            data = dict([(k, []) for k in keys])
        data['t'].append(eng.evolved_time)
        data['entropy'].append(eng.psi.entanglement_entropy())
        data['corr_Z'].append(eng.psi.correlation_function('Sigmaz', 'Sigmaz'))
        data['trunc_err'].append(eng.trunc_err.eps)
        return data

    data = measurement(eng, None)
    while eng.evolved_time < 20.:
        eng.run()
        measurement(eng, data)

    plt.figure()
    plt.plot(data['t'], np.array(data['entropy'])[:, L//2], label=name)
    plt.xlabel('time $t$')
    plt.ylabel('entropy $S$')
    plt.legend(loc='best')
    plt.savefig('PXP_entropy.png')

def TDVP(psi, model, name):
    tdvp_params = {
        'start_time': 0,
        'dt': 0.1,
        'N_steps': 1,
        'trunc_params': {
            'chi_max': 40,
            'svd_min': 1.e-10,
            'trunc_cut': None
        }
    }
    tdvp_engine = tdvp.TwoSiteTDVPEngine(psi, model, tdvp_params)
    times = []
    S_mid = []
    Es = []
    ZZ = []

    def measure():
        times.append(tdvp_engine.evolved_time)
        S_mid.append(psi.entanglement_entropy(bonds=[L // 2])[0])
        ZZ.append(psi.correlation_function('Sigmaz', 'Sigmaz'))

    measure()
    for i in range(100):
        tdvp_engine.run()
        measure()

    tdvp_engine = tdvp.SingleSiteTDVPEngine.switch_engine(tdvp_engine)
    for i in range(100):
        tdvp_engine.run()
        measure()

    plt.plot(times, S_mid, label=name)
    return times, S_mid


if __name__ == "__main__":
    tenpy.tools.misc.setup_logging(to_stdout="INFO")

    L = 12
    model_params = {
        'J': 1.,
        'L': L,
        'bc_x': 'periodic',
        'bc_MPS': 'finite'
    }
    M = PXPChain(model_params)
    p_state = ['up'] * L
    psi_0 = MPS.from_product_state(M.lat.mps_sites(), p_state, bc=M.lat.bc_MPS)
    p_state = ['up', 'down'] * (L // 2)
    psi_z2 = MPS.from_product_state(M.lat.mps_sites(), p_state, bc=M.lat.bc_MPS)
    p_state = ['up', 'up', 'down'] * (L // 3)
    psi_z3 = MPS.from_product_state(M.lat.mps_sites(), p_state, bc=M.lat.bc_MPS)
    p_state = ['up', 'up', 'up', 'down'] * (L // 4)
    psi_z4 = MPS.from_product_state(M.lat.mps_sites(), p_state, bc=M.lat.bc_MPS)

    plt.figure()
    # iTEBD(psi_z2, M, name='$Z_2$')
    times, S_mid_0 = TDVP(psi_0, M, name='$0$')
    times, S_mid_z2 = TDVP(psi_z2, M, name='$Z_2$')
    times, S_mid_z3 = TDVP(psi_z3, M, name='$Z_3$')
    times, S_mid_z4 = TDVP(psi_z4, M, name='$Z_4$')
    plt.xlabel('time $t$')
    plt.ylabel('entropy $S$')
    plt.legend(loc='best')
    plt.savefig('PXP_entropy.png')
