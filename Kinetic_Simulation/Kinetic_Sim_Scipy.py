from sqlite3 import Time
import numpy as np
from scipy import integrate as it
import math as ma
from matplotlib import pyplot as pp
import time

#!Const

Bol_c = 1.38065e-23
Plan_c = 6.626e-34
R_c = 0.0083145
k2h = 2.0837e10
Fa = 96485

#!Const_end
#!Parameters

c_Ni_0 = 6e-3 # Analytic concentration of the nickel catalyst: 6e-3 mmol/L
c_init_R1 = 6e-2
c_init_R2 = c_init_R1 * 3

Temp = 298.15
I_eff = 1e-2
Vol = 5e-3 # L
Rcat0 = I_eff / (Fa * Vol)

k_init1 = 5e-2
K_init1 = 1e3
k_init2 = 5e-2
K_init2 = 1e3

k_add1_1 = 1e8
K_add1_1 = 4e7
k_add1_2 = 1e8
K_add1_2 = 4e7

k_add2_11 = 3e7
K_add2_11 = 2e3
k_add2_12 = 3e7
K_add2_12 = 2e3
k_add2_21 = 3e7
K_add2_21 = 2e3
k_add2_22 = 3e7
K_add2_22 = 2e3

k_re_11 = 5e3
k_re_12 = 5e3
k_re_21 = 5e3
k_re_22 = 5e3

k_sc = 0 #1e9
k_Ni_re = 1

Tot_t = 21600  # s
Acc = 1e-4

#!Parameters_end
#!Func

def Keq(delG):
    return ma.exp(-delG * 4.184 / (R_c * Temp))

def kTST(Bar): # kcal/mol
    return k2h * Temp * ma.exp(-Bar * 4.184 / (R_c * Temp))

def test(t,u):
    k = 1
    ca, cb, caa, cab, cbb = u
    ra = - 2 * k * (ca ** 2) - k * ca * cb
    rb = - 2 * k * (cb ** 2) - k * ca * cb
    raa = k * (ca ** 2)
    rab = k * ca * cb
    rbb = k * (cb ** 2)
    ru = [ra, rb, raa, rab, rbb]
    return ru

def reqs(t, u): # Differential rate equations
    cNi0, cNi1, cR1Br, cR2Br, cR1, cR2, cNiR1, cNiR2, cNiR11, cNiR12, cNiR21, cNiR22, cR11, cR12, cR22 = u
    rNi0 = - k_init1 * cNi0 * cR1Br - k_init2 * cNi0 * cR2Br + k_init1 / K_init1 * cNi1 * cR1 + k_init2 / K_init2 * cNi1 * cR2 + Rcat0 * (1 - ma.exp( - cNi1 / Rcat0 * 10))
    rNi1 = k_init1 * cNi0 * cR1Br + k_init2 * cNi0 * cR2Br - k_init1 / K_init1 * cNi1 * cR1 + k_init2 / K_init2 * cNi1 * cR2 - k_add1_1 * cNi1 * cR1 - k_add1_2 * cNi1 * cR2 + k_add1_1 / K_add1_1 * cNiR1 + k_add1_2 / K_add1_2 * cNiR2 + k_re_11 * cNiR11 + k_re_12 * cNiR12 + k_re_21 * cNiR21 + k_re_22 * cNiR22 - Rcat0 * (1 - ma.exp( - cNi1 / Rcat0 * 10))
    rR1Br = - k_init1 * cNi0 * cR1Br  + k_init1 / K_init1 * cNi1 * cR1
    rR2Br = - k_init2 * cNi0 * cR2Br  + k_init2 / K_init2 * cNi1 * cR2
    rR1 = k_init1 * cNi0 * cR1Br - k_init1 / K_init1 * cNi1 * cR1 - k_add1_1 * cR1 * cNi1 + k_add1_1 / K_add1_1 * cNiR1 - k_add2_11 * cR1 * cNiR1 - k_add2_21 * cR1 * cNiR2 + k_add2_11 / K_add2_11 * cNiR11 + k_add2_21 / K_add2_21 * cNiR21 - 2 * k_sc * (cR1 ** 2) - k_sc * cR1 * cR2
    rR2 = k_init2 * cNi0 * cR2Br - k_init2 / K_init2 * cNi1 * cR2 - k_add1_2 * cR2 * cNi1 + k_add1_2 / K_add1_2 * cNiR2 - k_add2_12 * cR2 * cNiR1 - k_add2_22 * cR2 * cNiR2 + k_add2_12 / K_add2_12 * cNiR12 + k_add2_22 / K_add2_22 * cNiR22 - 2 * k_sc * (cR2 ** 2) - k_sc * cR1 * cR2
    rNiR1 = k_add1_1 * cR1 * cNi1 - k_add1_1 / K_add1_1 * cNiR1 - k_add2_11 * cR1 * cNiR1  - k_add2_12 * cR2 * cNiR1 + k_add2_11 / K_add2_11 * cNiR11 + k_add2_12 / K_add2_12 * cNiR12
    rNiR2 = k_add1_2 * cR2 * cNi1 - k_add1_2 / K_add1_2 * cNiR2 - k_add2_21 * cR1 * cNiR2  - k_add2_22 * cR2 * cNiR2  + k_add2_21 / K_add2_21 * cNiR21 + k_add2_22 / K_add2_22 * cNiR22
    rNiR11 = k_add2_11 * cR1 * cNiR1 - k_add2_11 / K_add2_11 * cNiR11 - k_re_11 * cNiR11
    rNiR12 = k_add2_12 * cR2 * cNiR1 - k_add2_12 / K_add2_12 * cNiR12 - k_re_12 * cNiR12
    rNiR21 = k_add2_21 * cR1 * cNiR2 - k_add2_21 / K_add2_21 * cNiR21 - k_re_21 * cNiR21
    rNiR22 = k_add2_22 * cR2 * cNiR2 - k_add2_22 / K_add2_22 * cNiR22 - k_re_22 * cNiR22
    rR11 = k_re_11 * cNiR11 + k_sc * (cR1 ** 2)
    rR12 = k_re_12 * cNiR12 + k_re_21 * cNiR21 + 2 * k_sc * cR1 * cR2
    rR22 = k_re_22 * cNiR22 + k_sc * (cR2 ** 2)
    ru = [rNi0, rNi1, rR1Br, rR2Br, rR1, rR2, rNiR1, rNiR2, rNiR11, rNiR12, rNiR21, rNiR22, rR11, rR12, rR22]
    return ru

#!Func_end
#!Solve

Time_start = time.time()
Record_interval = ma.ceil(1 / Acc)
Tscale = 60
Low_limit = 100
U0 = [0.0, c_Ni_0, c_init_R1, c_init_R2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
Utest = [0.1, 0.3, 0.0, 0.0, 0.0]

N = len(U0)
Count = ma.ceil(Tot_t / Acc)
Count2 = ma.ceil(Count / Record_interval)
t = np.linspace(0, Tot_t, Count)
T1 = np.linspace(0, Tot_t, Count2) / Tscale

solve = it.odeint(reqs, U0, t, tfirst = True, tcrit = [])

#!Solve_end
#!Processing

Solve = np.zeros((N + 1) * Count2).reshape(Count2, N + 1)
Solve[:,0] = T1
Sl = slice(0, Count, Record_interval)
for i in range(1, N+1):
    Solve[:,i] = solve[:,i-1][Sl]

Count3 = Count2 - Low_limit
T2 = T1[Low_limit:].reshape(-1)
r_12_11 = (Solve[Low_limit:,14] / Solve[Low_limit:,13]).reshape(-1)
r_22_11 = (Solve[Low_limit:,15] / Solve[Low_limit:,13]).reshape(-1)

Sel = np.zeros(3 * Count3).reshape(Count3, 3)
Sel[:,0] = T2
Sel[:,1] = r_12_11
Sel[:,2] = r_22_11
Ones = np.ones(Count3)

CR_1 = round(1 - Solve[:,3][-1] / c_init_R1, 4)
CR_2 = round(1 - Solve[:,4][-1] / c_init_R2, 4)
R_12_11 = round(r_12_11[-1], 4)
R_22_11 = round(r_22_11[-1], 4)
Y11 = round(2 / (R_12_11 + 2) * CR_1, 4)
Y12 = round(R_12_11 / (R_12_11 + 2) * CR_1, 4)
Y22 = round(2 * Solve[:, 15][-1] / c_init_R2, 4)
Yield = f'*Final R12/R11 = {R_12_11}\n*R22/R11 = {R_22_11}\n*Conversion Rate of RBr_1 = {CR_1}\n*Conversion Rate of RBr_2 = {CR_2}\n*Yield of R_11 = {Y11}\n*Yield of R_12 = {Y12}\n*Yield of R_22 = {Y22}\n'

Time_end = time.time()
Time_end_asc = time.ctime(Time_end)
Time_elapsed = round(Time_end - Time_start, 0)
Time = f'*Time_end = {Time_end_asc}\n*Time_elapsed = {Time_elapsed} sec\n'

#!Processing_end
#!Output

np.savetxt("res.csv", Solve, delimiter = ',')
np.savetxt("selectivity.csv", Sel, delimiter = ',')
print(Yield + Time)
G = open('Kinetic_Sim_Scipy.py', 'r')
Gread = G.read().split('#!Parameters')[1]
F = open('__Yield__.out', 'w')
F.write(Yield + Time + Gread)
F.close()

#!Output_end
#!Plotting

pp.figure(figsize=(8, 6))

pp.subplot(1, 2, 1)
pp.plot(T1, Solve[:,3], label = 'c_R1Br')
pp.plot(T1, Solve[:,4], label = 'c_R2Br')
pp.plot(T1, Solve[:,13], label = 'c_R1R1')
pp.plot(T1, Solve[:,14], label = 'c_R1R2')
pp.plot(T1, Solve[:,15], label = 'c_R2R2')
pp.legend(loc = "upper right")
pp.xlabel('Time (min)')
pp.ylabel('Concentration (M)')

pp.subplot(1, 2, 2)
pp.plot(T2, Sel[:,1], label = 'c_R1R2/c_R1R1')
pp.plot(T2, Sel[:,2], label = 'c_R2R2/c_R1R1')
pp.plot(T2, Ones, label = 'Baseline')
pp.legend(loc = "center right")
pp.xlabel('Time (min)')
pp.ylabel('Ratio')

pp.savefig('RES.png')
pp.show() # May not be shown in Linux

#!Plotting_end
