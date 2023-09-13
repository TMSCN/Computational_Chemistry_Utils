import os
import time
import math as m
from scipy.optimize import minimize

Temperature = 298.15 # K
Ad = 0.0001438775/Temperature # hc/kT, unit: cm
Z = 5.9811E-3 # 0.5*hcL*1E-3*100
dir = os.getcwd()
allFile = os.listdir(dir)
TIME = time.asctime()

testSetExp = {
    'HF':[3959],
    'H2':[4159],
    'N2':[2330],
    'F2':[894],
    'CO':[2143],
    'OH':[3568],
    'Cl2':[554],
    'N2O':[589, 589, 1285, 2224],
    'CO2':[667, 667, 1333, 2349],
    'H2O':[1659, 3657, 3756],
    'CH4':[1306, 1306, 1306, 1534, 1534, 2917, 3019, 3019, 3019],
    'C2H2':[612, 612, 730, 730, 1974, 3289, 3374],
    'C2H4':[825, 943, 949, 1023, 1236, 1342, 1444, 1623, 2989, 3026, 3103, 3106],
    'C2H6':[289, 822, 822, 995, 1190, 1190, 1379, 1388, 1468, 1468, 1469, 1469, 2896, 2954, 2969, 2969, 2985, 2985],
    'CH3OH':[250, 1033, 1060, 1165, 1345, 1455, 1477, 1477, 2844, 2960, 3000, 3681],
    'CH2O':[1167, 1249, 1500, 1746, 2782, 2843],
    'HCN':[712, 712, 2097, 3311],
    'HCOOH':[625, 638, 1033, 1105, 1229, 1387, 1770, 2943, 3570],
    'HNCO':[610, 643, 762, 1327, 2274, 3531],
    'NH3':[950, 1627, 1627, 3337, 3444, 3444],
    'HOBr':[626, 1164, 3590], # 1990
    'NO2Br':[282, 290, 606, 783, 1291, 1659], # A
    'CBr2':[196, 595, 641], # B
    'CH2Cl2':[282, 717, 758, 898, 1153, 1268, 1467, 2999, 3040],
    'CH3Cl':[732, 1017, 1017, 1355, 1452, 1452, 2937, 3039, 3039],
    'PH':[2276],
    'SH':[2592]
} # 测试集实验频率，ref: Shimanouchi, T. J. Phys. Chem. Ref. Data 1977, 6, 993

testSetExpZPE = {
    'H2':25.98,
    'OH':22.09,
    'HF':24.48,
    'PH':14.02,
    'SH':16.02,
    'N2':14.06,
    'F2':5.44,
    'CO':12.93,
    'Cl2':3.35,
    'HCN':41.63,
    'C2H2':68.87,
    'C2H4':131.67,
    'CH2O':69.16,
    'CH4':115.94,
    'CH3Cl':98.11,
    'H2O':55.44,
    'NH3':89.24,
    'N2O':28.49
} # Unit: kJ/mol
    
def scriptor(s):
    return s.split('.')[-1]

def getVibCount(Ex = testSetExp):
    length = 0
    for key in Ex:
        length += len(Ex[key])
    return length

testSetTheor = {}
testSetTheorZPE = {}

def getZPETheorCount(Ex = testSetExpZPE):
    length = len(Ex)
    for key in Ex:
        filename = key + '.log'
        if not filename in allFile:
            length -= 1
    return length
    
def readFreq(e): #读取log文件中的理论谐振频率值
    res = []
    e1 = e.split('normal coordinates:')[1]
    e2 = e1.split(' - Thermochemistry -')[0]
    columns = e2.split('\n')
    for c in columns:
        if 'Frequencies' in c:
            c1 = c.split()[2:]
            for d in c1:
                data = round(float(d),1)
                res.append(data)
    return res

def generateVibDict(): #生成测试集的理论谐振频率字典
    res = {}
    for filename in os.listdir(dir):
        if scriptor(filename) != 'log':
            continue
        name = filename.split('.')[0]
        f = open(filename)
        text = f.read()
        freq = readFreq(text)
        res.update({name:freq})
        f.close()
    return res

testSetTheor = generateVibDict()
len_testSetTheor = len(testSetTheor)
len_testSetExp = len(testSetExp)
len_testSetTheorVib = getVibCount(testSetTheor)
len_testSetExpVib = getVibCount()
len_testSetTheorZPE = getZPETheorCount()
len_testSetExpZPE = len(testSetExpZPE)

def fundamentalFactor(Th = testSetTheor, Ex = testSetExp): #直接生成基频校正因子
    Sq = 0
    Cr = 0
    for mol in Th:
        vibT = Th[mol]
        vibE = Ex[mol]
        length = len(vibT)
        if len(vibE) != length:
            print(f'Exception in {mol}!')
            continue
        for i in range(0,length):
            Cr += vibT[i]*vibE[i]
            Sq += pow(vibT[i], 2)
    return Cr/Sq

def ZPE(freqs):
    res = 0
    for v in freqs:
        res += v*Z
    return res

def enthalpyVib(x): #振动内能，前面的常数省略了
    return x/(m.exp(Ad*x) - 1)/10000 #为了保证优化算法成功运行在后边除以了10000

def entropyVib(x): #振动熵，前面的常数省略了
    return Ad*x/(m.exp(Ad*x)-1) - m.log(1-m.exp(-Ad*x))

def ZPEError(x, lib = testSetExpZPE):
    D = 0
    for mol in lib:
        ZPE_Exp = lib[mol]
        filename = mol + '.log'
        if not filename in allFile:
            print(f'{filename} is not in the directory.')
            continue
        f = open(filename)
        text = f.read()
        freq = readFreq(text)
        ZPE_Theor = ZPE(freq)
        D += pow(x*ZPE_Theor - ZPE_Exp,2)
    return D
    
def enthalpyError(x, Th = testSetTheor, Ex = testSetExp): #振动焓残差平方和
    D = 0
    for mol in Th:
        vibT = Th[mol]
        vibE = Ex[mol]
        length = len(vibT)
        if len(vibE) != length:
            print(f'Exception in {mol}!')
            continue
        for i in range(0,length):
            D += pow(enthalpyVib(x*vibT[i]) - enthalpyVib(vibE[i]), 2)
    return D

def entropyError(x, Th = testSetTheor, Ex = testSetExp): #振动熵残差平方和
    D = 0
    for mol in Th:
        vibT = Th[mol]
        vibE = Ex[mol]
        length = len(vibT)
        if len(vibE) != length:
            print(f'Exception in {mol}!')
            continue
        for i in range(0,length):
            D += pow(entropyVib(x*vibT[i]) - entropyVib(vibE[i]), 2)
    return D

def writeLog(filename, text, mode = 'a'):
    f = open(filename + '.out', mode)
    f.write(text)
    f.close()

guess = 0.95
fname = 'scaleRes'
texts = f'''\
Running ScaleGenerator...
There are {len_testSetExp} molecules and {len_testSetExpVib} frequencies in the experimental set of frequencies.
There are {len_testSetTheor} molecules and {len_testSetTheorVib} frequencies in the theoretical set of frequencies.
There are {len_testSetExpZPE} data in the experimental set of ZPEs.
There are {len_testSetTheorZPE} loaded data in the theoretical set of ZPEs.
Initial guess of minimizing function is {guess}.
Running minimizing function...

'''
writeLog(fname, texts, 'w')

fundamentalFactor =  fundamentalFactor()
ZPEFactor = minimize(ZPEError, guess)
enthalpyFactor = minimize(enthalpyError, guess) #寻找残差平方和的在x=guess附近的极小值点
entropyFactor = minimize(entropyError, guess)
LZPE = ZPEFactor.x[0]
LU = enthalpyFactor.x[0]
LS = entropyFactor.x[0]

texts = f'''\
Scale factor of fundamental frequencies = {fundamentalFactor}
Scale factor of ZPE = {LZPE}
Scale factor of thermal energy (U) = {LU}
Scale factor of entropy (S) ={LS}

Normal termination in {TIME}.

'''
writeLog(fname, texts)

