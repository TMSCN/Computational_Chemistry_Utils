import numpy as np
from scipy import integrate as it
import math as ma
import multiprocessing as mp
#import matplotlib; matplotlib.use('TkAgg')
from matplotlib import pyplot as pp

Bol_c = 1.38065e-23
Plan_c = 6.626e-34
R_c = 0.0083145
k2h = 2.0837e10

c_Ni_0 = 6e-3 # Analytic concentration: 6e-3 mmol/L
c_init_R1 = 6e-2
c_init_R2 = c_init_R1 * 3

Temp = 298.15
Fa = 96485
I_eff = 1e-2
Vol = 5e-3
Rcat0 = I_eff / (Fa * Vol)

k_init1 = 5e-2
K_init1 = 1e3
k_init2 = 5e-2
K_init2 = 1e3

k_add1_1 = 1e8
K_add1_1 = 4e7
k_add1_2 = 1e8
K_add1_2 = 4e7

k_add2_11 = 2e7
K_add2_11 = 2e3
k_add2_12 = 2e7
K_add2_12 = 2e3
k_add2_21 = 2e7
K_add2_21 = 2e3
k_add2_22 = 2e7
K_add2_22 = 2e3

k_re_11 = 5e3
k_re_12 = 5e3
k_re_21 = 5e3
k_re_22 = 5e3

k_sc = 0 #1e9
k_Ni_re = 1

Tot_t = 21600  # s
Acc = 1e-4
Record_interval = ma.ceil(1 / Acc)
tscale = 60
N = 15

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

def reqs(t, u):
    #Rcat = Rcat0
    #if u[1] < 1e-6:
    #    Rcat = 0
    cNi0, cNi1, cR1Br, cR2Br, cR1, cR2, cNiR1, cNiR2, cNiR11, cNiR12, cNiR21, cNiR22, cR11, cR12, cR22 = u
    rNi0 = - k_init1 * cNi0 * cR1Br - k_init2 * cNi0 * cR2Br + k_init1 / K_init1 * cNi1 * cR1 + k_init2 / K_init2 * cNi1 * cR2 + Rcat0 * (1 - ma.exp( - cNi1 / Rcat0 * 10))
    rNi1 = k_init1 * cNi0 * cR1Br + k_init2 * cNi0 * cR2Br - k_init1 / K_init1 * cNi1 * cR1 + k_init2 / K_init2 * cNi1 * cR2 - k_add1_1 * cNi1 * cR1 - k_add1_2 * cNi1 * cR2 + k_add1_1 / K_add1_1 * cNiR1 + k_add1_2 / K_add1_2 * cNiR2 + k_re_11 * cNiR11 + k_re_12 * cNiR12 + k_re_21 * cNiR21 + k_re_22 * cNiR22 - Rcat0 * (1 - ma.exp( - cNi1 / Rcat0 * 10))
    rR1Br = - k_init1 * cNi0 * cR1Br  + k_init1 / K_init1 * cNi1 * cR1
    rR2Br = - k_init2 * cNi0 * cR2Br  + k_init2 / K_init2 * cNi1 * cR2
    rR1 = k_init1 * cNi0 * cR1Br - k_init1 / K_init1 * cNi1 * cR1 - k_add1_1 * cR1 * cNi1 + k_add1_1 / K_add1_1 * cNiR1 - k_add2_11 * cR1 * cNiR1 - k_add2_12 * cR1 * cNiR2 + k_add2_11 / K_add2_11 * cNiR11 + k_add2_12 / K_add2_12 * cNiR12 - 2 * k_sc * (cR1 ** 2) - k_sc * cR1 * cR2
    rR2 = k_init2 * cNi0 * cR2Br - k_init2 / K_init2 * cNi1 * cR2 - k_add1_2 * cR2 * cNi1 + k_add1_2 / K_add1_2 * cNiR2 - k_add2_21 * cR2 * cNiR1 - k_add2_22 * cR2 * cNiR2 + k_add2_21 / K_add2_21 * cNiR21 + k_add2_22 / K_add2_22 * cNiR22 - 2 * k_sc * (cR2 ** 2) - k_sc * cR1 * cR2
    rNiR1 = k_add1_1 * cR1 * cNi1 - k_add1_1 / K_add1_1 * cNiR1 - k_add2_11 * cNiR1 * cR1 - k_add2_12 * cNiR1 * cR2 + k_add2_11 / K_add2_11 * cNiR11 + k_add2_12 / K_add2_12 * cNiR12
    rNiR2 = k_add1_2 * cR2 * cNi1 - k_add1_2 / K_add1_2 * cNiR2 - k_add2_21 * cNiR2 * cR1 - k_add2_22 * cNiR2 * cR2 + k_add2_21 / K_add2_21 * cNiR21 + k_add2_22 / K_add2_22 * cNiR22
    rNiR11 = k_add2_11 * cR1 * cNiR1 - k_add2_11 / K_add2_11 * cNiR11 - k_re_11 * cNiR11
    rNiR12 = k_add2_12 * cR1 * cNiR2 - k_add2_12 / K_add2_12 * cNiR12 - k_re_12 * cNiR12
    rNiR21 = k_add2_21 * cR2 * cNiR1 - k_add2_21 / K_add2_21 * cNiR21 - k_re_21 * cNiR21
    rNiR22 = k_add2_22 * cR2 * cNiR2 - k_add2_22 / K_add2_22 * cNiR22 - k_re_22 * cNiR22
    rR11 = k_re_11 * cNiR11 + k_sc * (cR1 ** 2)
    rR12 = k_re_12 * cNiR12 + k_re_21 * cNiR21 + 2 * k_sc * cR1 * cR2
    rR22 = k_re_22 * cNiR22 + k_sc * (cR2 ** 2)
    ru = [rNi0, rNi1, rR1Br, rR2Br, rR1, rR2, rNiR1, rNiR2, rNiR11, rNiR12, rNiR21, rNiR22, rR11, rR12, rR22]
    return ru

Low_limit = 100
U0 = [0.0, c_Ni_0, c_init_R1, c_init_R2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
Utest = [0.1, 0.3, 0.0, 0.0, 0.0]
#Ut2 = [4.094671571069439516e-05,5.958563513233787121e-03,5.999987755056837568e-02,1.799996326517050993e-01,7.207556513681074210e-13,2.162250441862488604e-12,1.224436128713862064e-07,3.673274403685983238e-07,1.324078274026293825e-16,5.296404613228994050e-16,1.191649260213422060e-15,8.495299556687493026e-13,3.398178003999437672e-12,7.645634218410373917e-12]

Count = ma.ceil(Tot_t / Acc)
Count2 = ma.ceil(Count / Record_interval)
t = np.linspace(0, Tot_t, Count)
T1 = np.linspace(0, Tot_t, Count2) / tscale

solve = it.odeint(reqs, U0, t, tfirst = True, tcrit = [])

Solve = np.zeros((N + 1) * Count2).reshape(Count2, N + 1)
Solve[:,0] = T1
Sl = slice(0, Count, Record_interval)
for i in range(1, N+1):
    Solve[:,i] = solve[:,i-1][Sl]

Count3 = Count2 - Low_limit
T2 = T1[Low_limit:].reshape(-1)
#r_12_11 = (Solve[Low_limit:,4] / Solve[Low_limit:,3]).reshape(-1)
#r_22_11 = (Solve[Low_limit:,5] / Solve[Low_limit:,3]).reshape(-1)
#r_12_11 = (Solve[Low_limit:,4] / Solve[Low_limit:,3]).reshape(-1)
#r_22_11 = (Solve[Low_limit:,8] / Solve[Low_limit:,7]).reshape(-1)
r_12_11 = (Solve[Low_limit:,14] / Solve[Low_limit:,13]).reshape(-1)
r_22_11 = (Solve[Low_limit:,15] / Solve[Low_limit:,13]).reshape(-1)
r_12 = (Solve[Low_limit:,6] / Solve[Low_limit:,5]).reshape(-1)

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
print(Yield)

np.savetxt("res.csv", Solve, delimiter = ',')
np.savetxt("selectivity.csv", Sel, delimiter = ',')
f = open('Yield.txt', 'w')
f.write(Yield)
f.close()

pp.figure(figsize=(10, 8))

pp.subplot(2, 2, 1)
pp.plot(T1, Solve[:,3], label = 'c_R1Br')
pp.plot(T1, Solve[:,4], label = 'c_R2Br')
pp.plot(T1, Solve[:,13], label = 'c_R1R1')
pp.plot(T1, Solve[:,14], label = 'c_R1R2')
pp.plot(T1, Solve[:,15], label = 'c_R2R2')
pp.legend(loc = "upper right")
pp.xlabel('Time (min)')
pp.ylabel('Concentration (M)')

pp.subplot(2, 2, 2)
pp.plot(T2, Sel[:,1], label = 'c_R1R2/c_R1R1')
pp.plot(T2, Sel[:,2], label = 'c_R2R2/c_R1R1')
pp.plot(T2, Ones, label = 'Baseline')
pp.legend(loc = "center right")
pp.xlabel('Time (min)')
pp.ylabel('Ratio')

pp.subplot(2, 2, 3)
pp.plot(T1, Solve[:,5], label = 'cR1')
pp.plot(T1, Solve[:,6], label = 'cR2')
pp.legend(loc = "center left")
pp.xlabel('Time (min)')
pp.ylabel('Concentration (M)')

pp.subplot(2, 2, 4)
pp.plot(T2, r_12, label = 'c_R2/c_R1')
pp.plot(T2, Ones, label = 'Baseline')
pp.legend(loc = "center right")
pp.xlabel('Time (min)')
pp.ylabel('Ratio')

pp.savefig('RES.png')
pp.show() # May not be shown in Linux


