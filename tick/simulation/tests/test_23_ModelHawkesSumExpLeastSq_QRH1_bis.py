# License: BSD 3 clause

import numpy as np
from tick.simulation import HawkesKernelSumExp
from tick.simulation import SimuHawkes

n_nodes = 2
dim = n_nodes
seed = 1000
MaxN_of_f = 5
f_i = [np.array([1., 1., 1., 1., 1.]), np.array([1., 1., 1., 1., 1.])]

end_time = 100000
betas = np.array([0.1, 2, 5])

U = len(betas)
kernels = np.array([
            [HawkesKernelSumExp(np.array([0.2, 0.15, 0.1]), betas), HawkesKernelSumExp(np.array([0.3, 0.1, 0.1]), betas)],
            [HawkesKernelSumExp(np.array([0., 0.2, 0.0]), betas), HawkesKernelSumExp(np.array([0., 0.4, 0.1]), betas)]
        ])

simu_model = SimuHawkes(kernels=kernels, end_time=end_time, custom=True, seed=seed, MaxN_of_f=MaxN_of_f, f_i=f_i)
for i in range(n_nodes):
    simu_model.set_baseline(i, 0.4 + 0.1 * i)
    for j in range(n_nodes):
        simu_model.set_kernel(i, j, kernels[i, j])
simu_model.track_intensity(0.1)
simu_model.simulate()

# plot_point_process(simu_model)
print("Timestamps:", len(simu_model.timestamps[0]), len(simu_model.timestamps[1]))
##################################################################################################################





##################################################################################################################
timestamps = simu_model.timestamps

from tick.optim.model import ModelHawkesFixedSumExpKernLeastSqQRH1, ModelHawkesFixedSumExpKernLeastSq
org_model = ModelHawkesFixedSumExpKernLeastSq(betas)
org_model.fit(timestamps, end_time)

timestamps.append(np.array([]))
global_n = np.array(simu_model._pp.get_global_n())
global_n = np.insert(global_n, 0, 0).astype(int)

print("global_n:", len(global_n))

model = ModelHawkesFixedSumExpKernLeastSqQRH1(betas, MaxN_of_f, n_threads=4)
model.fit(timestamps, global_n, end_time)
#############################################################################

x_real = np.array(
    [0.4, 0.5,   0.2, 0.3, 0, 0,   0.15, 0.1, 0.2, 0.4,   0.1, 0.1, 0., 0.1,
     1., 1., 1., 1., 1.,     1., 1., 1., 1., 1.])
x_real_2 = np.array(
    [0.4, 0.5,   0.2, 0.15, 0.1,     0.3, 0.1, 0.1,     0., 0.2, 0.0,     0., 0.4, 0.1,
     1., 1., 1., 1., 1.,     1., 1., 1., 1., 1.])
x_real_org = np.array(
    [0.4, 0.5,   0.2, 0.15, 0.1,     0.3, 0.1, 0.1,     0., 0.2, 0.0,     0., 0.4, 0.1])


x0 = np.ones(len(x_real_org)) * 0.5
x03 = np.ones(len(x_real_2)) * 0.5

print('#' * 40)
print(model.loss(x_real_2))
print(org_model.loss(x_real_org))

############################################################################
from scipy.optimize import minimize
res = minimize(org_model.loss, x0, method='Nelder-Mead', tol=1e-6, options={'maxiter':100000})
print('#' * 40)
print('scipy.optimize.minimize')
print(res.x)
print(org_model.loss(res.x))

###########################################################################
from scipy.optimize import minimize
res = minimize(model.loss, x03, method='Nelder-Mead', tol=1e-6, options={'maxiter':100000})
print('#' * 40)
print('scipy.optimize.minimize')

coeff = res.x
for k in range(dim):
    fi0 = coeff[dim + U * dim * dim + k * MaxN_of_f]
    coeff[k] *= fi0
    coeff[dim + U * dim * k: dim + U * dim * (k + 1)] *= fi0
    coeff[dim + U * dim * dim + k * MaxN_of_f: dim + U * dim * dim + (k + 1) * MaxN_of_f] /= fi0
print(coeff)
print(model.loss(res.x))


############################################################################
from tick.optim.solver import AGD
from tick.optim.prox import ProxZero, ProxL1

# print('#' * 40)
# print('tick.agd')
# prox = ProxZero()
# solver = AGD(step=1e-3, linesearch=False, max_iter=5000, print_every=50)
# solver.set_model(org_model).set_prox(prox)
# x0 = np.array(
#     [0.6, 0.8,   0.2, 0.2, 0.2, 0.2,  0.4, 0.4, 0.4, 0.4, 0.5, 0.5, 0.5, 0.5])
# solver.solve(x0)
#
# print(org_model.loss(solver.solution))
# print(solver.solution)


# print('#' * 40)
# print('tick.agd')
# prox = ProxZero()
# solver = AGD(step=1e-3, linesearch=False, max_iter=5000, print_every=50)
# solver.set_model(model).set_prox(prox)
# solver.solve(x02)
#
# coeff = solver.solution
# for k in range(dim):
#     fi0 = coeff[dim + U * dim * dim + k * MaxN_of_f]
#     coeff[k] *= fi0
#     coeff[dim + U * dim * k: dim + U * dim * (k + 1)] *= fi0
#     coeff[dim + U * dim * dim + k * MaxN_of_f: dim + U * dim * dim + (k + 1) * MaxN_of_f] /= fi0
# print(coeff)
# print(org_model.loss(solver.solution))