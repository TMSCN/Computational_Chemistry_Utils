# Import Area =================================================================

import os
from sys import argv

# Functions' Area ==============================================================

def scriptor(s):
    if '.' not in s:
        return 0
    return s.split('.')[-1]

def submit(o):
    cd = 'cd res'
    cdb = 'cd ..'
    chmod = 'chmod 750 -R *'
    g16=''
    formchk=''
    for i in o:
        g16 += f'g16 {i}.gjf\n'
        # formchk += f'formchk {i}.chk\n'
    text = f'''\
{cd}
{chmod}
{g16}
{chmod}
{formchk}
{cdb}
'''
    f = open('.g16SubmitHRSP','w')
    f.write(text)
    f.close()

def BatchSubmit(o):
    text = '('
    sp = ' '
    for i in o:
        text += i
        text += sp
    text = text[:-1]
    text += ')'
    with open('BatchSubmit.txt','w') as f:
        f.write(text)
        f.close()
    
def getName(filename):
    sname = filename.split('.')[:-1]
    name = '.'.join(sname)
    return name

def inputParams(Param):
    res = ''
    if Param:
        res = '=('
        for key in Param.keys():
            output_option += key
            if Param[key] != 0 or Param[key] != None or Param[key] != False:
                output_option += ('=' + str(Param[key]) + ',')
        res = res[:-1]
        res += ')'
    return res

# Parameters' Input Area =========================================================
   
element_dict = {'H':1,'He':2,'Li':3,'Be':4,'B':5,'C':6,'N':7,'O':8,'F':9,'Ne':10,
                'Na':11,'Mg':12,'Al':13,'Si':14,'P':15,'S':16,'Cl':17,'Ar':18,'K':19,'Ca':20,
                'Sc':21,'Ti':22,'V':23,'Cr':24,'Mn':25,'Fe':26,'Co':27,'Ni':28,'Cu':29,'Zn':30,
                'Ga':31,'Ge':32,'As':33,'Se':34,'Br':35,'Kr':36,'I':53} #周期表

nproc = 10 #调用核数
mem = 12 #调用内存大小(GB)
opt = True
opt_option = {

}
freq = True
freq_option = {

}
output_option = 'p' #输出信息选项，''为默认，'p'为详细信息
method = 'M062X' #方法/泛函名，注意是否前面得加U或RO
basis_name = 'def2SVP' #基组名
basis_built_in = True #是否Gaussian为内置基组
basis_dir = 'D:/!Academic Resources/!!Researches/!Databases/Basis/' #基组库路径
ecp_used = False #是否使用赝势
ecp_used_for_3d = False #是否对第一过渡金属使用赝势
int_accuracy = 'ultrafine' #积分格点精度
scf_conver = 0 #收敛限制，写0是默认
scrf_enabled = False #是否启用溶剂化
scrf_read = True
solvent = 'ch3cn' #溶剂名，一定要检查！！！！！！！！！！！！！
solvation_model = 'SMD' #溶剂化模型
pop_model = '' #布居分析模型
empirical_dispersion = 'gd3'
guess = '' #guess选项，一般留空，用前一定检查！

supplement = f'''\
noneq=write
''' #补充输入

# Parameters' Pretreatment Area ====================================================  

connect = '****\n'
dir = os.getcwd()
testSetDir = dir + '\\testSet'
outputList=[]
sp = ' '

if basis_built_in:
    gen = basis_name
else:
    gen = 'gen'
    if ecp_used:
        gen = 'genecp'
    g = open(basis_dir+f'{basis_name}.txt')
    res = g.read()
    g.close()
    bases = res.split(connect)

output_option += (sp + method + sp + gen)

if opt:
    output_option += (sp + 'opt' + inputParams(opt_option))

if freq:
    output_option += (sp + 'freq' + inputParams(freq_option))

if int_accuracy != '':
    output_option += (sp + f'int={int_accuracy}')

if pop_model != '':
    output_option += (sp + f'pop={pop_model}')

if scf_conver > 0:
    output_option += (sp + f'scf=(conver={scf_conver})')

if scrf_enabled:
    output_option += (sp + f'scrf=({solvation_model},solvent={solvent},read)')

if empirical_dispersion != '':
    output_option += (sp + f'em={empirical_dispersion}')

if guess != '':
    output_option += (sp + f'guess={guess}')

# Processors' Area ===================================================================

def generate(inputDir = testSetDir, outputDir = f'{dir}\\TestSet'):
    for filename in os.listdir(inputDir):
        if scriptor(filename) != 'gjf':
            continue
        if filename[0] == '_':
            continue
        if filename[0] == '.':
            continue
        name = getName(filename)
        title = name
        outputList.append(title)
        file = open(inputDir + '\\' + filename)
        tmp = file.readline()
        while True:
            tmp = file.readline()
            if tmp[0].isdigit() == True or tmp[0] == '-':
                break
        multiplicity = tmp[:-1]
        coordinate=''
        element=set()
        temp=file.readline()
        while temp!='\n':
            element.add(temp.split(' ')[1])
            coordinate+=temp
            temp=file.readline()
        data=f'''\
%chk={title}.chk
%mem={mem}GB
%nprocshared={nproc}
#{output_option}

{title}

{multiplicity}
{coordinate}
'''
        if not basis_built_in:
            e = list(element_dict.keys())
            for i in e:
                if i in element:
                    j = e.index(i)
                    data+=bases[j]
                    data+=connect
            data=data[:-5]
            data+=connect
            data+=f'\n{supplement}'
        
        data+='\n\n&'
        file.close()
    
        newfile = open(outputDir + '\\' + f'{title}.gjf','w')
        newfile.write(data)
        newfile.close()
        print(f'{title}.gjf has been output successfully.')

generate()

#submit(outputList)
submit(outputList)
