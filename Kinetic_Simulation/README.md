#### What is required to run this program (Kinetic_Sim_Scipy.py)?
1. Ensure `Python3` has been installed on your system. `Python3.11` or later versions are recommended.
2. Ensure the following Python extension packages have been installed. If any of them is absent, try to run the command `pip install <package_name>` or `python -m pip install <package_name>` on the terminal.  Command `pip list` can list out all the installed Python extension packages.
	- `NumPy`(1.26.0 or greater)
	- `SciPy`(1.11.2 or greater)
	- `Matplotlib` (3.8.0 or greater)
3. A Python IDE, such as `VSCode`, `Jupyter`, or `PyCharm`, is recommended but not necessary.

After these preparations, the `Kinetic_Sim_Scipy.py` can be opened and run in a Python IDE, or run in the terminal with the following command:
```python <path/to/this/python/file>/Kinetic_Sim_Scipy.py```

**WARNING: Without any change in this code, this program may proceed slowly, or even have the system crashed with low computer specifications. Running on a high-performance server with the original settings, or adjusting the running parameters is recommended.**

### What is the output of this program?
After several minutes, upon the program finishing normally, 4 output files will be generated in the same directory of the `Kinetic_Sim_Scipy.py`:
- `res.csv`: A table recording the time of dynamic simulation (min, the first column), and the time-dependent concentrations (mol/L) of all substrates, products, and intermediates. The table `res.csv` is the essential output of this program.
- `selectivity.csv`: A table recording the time of dynamic simulation (min, the first column), and the time-dependent ratios of products.
- `RES.png`: A .png file showing concentrate-to-time curves of substrates & products (left), and ratios of products varying with time (right). A window showing this diagram may pop up upon the program finished.
- `__Yield__.out`: A plain text file recording: the final ratios of products' concentrations, conversion rate of substrates, simulated yields of products, the elapsed time to run this program, and the values of parameters. Part of its content will be also printed in the terminal.

### How to adjust the parameters in the dynamic simulation program?

The `!Const` block records physic chemistry constants in SI units, and it shouldn't be changed. `k2h` is the value of Boltzmann constant $k$ divided by Planck constant $h$.

In the `!Paramters` block, the following parameters are set. Adjusting these parameters should make an impact on the final results:
- The initial concentration of starting materials: `c_Ni_0`, `c_init_R1`, `c_init_R2` (mol/L)
	**Note**: The `U0` in the `!Solve` block is the variable that directly controls the initial concentrations of all reagents, intermediates, and products. `c_Ni_0`, `c_init_R1`, `c_init_R2` are contained in `U0`.
- Temperature: `Temp` (K)
- Reaction current: `I_eff` (A)
- Reaction volume: `Vol` (L)
- Forward rate constants of defined elementary reactions: `k_*`
- Forward equilibrium constants of defined elementary reactions: `K_*`
- Total simulation duration: `Tot_t`(s)
- Accuracy of the simulated curve: `Acc` (Must be greater than 0)
	**Note**: The last parameter `Acc` changes the time interval to solve differential rate equations numerically, and also the time interval to record concentration changes in `res.csv`. The lesser `Acc` is, the finer the time interval is. However, increasing `Acc` (not too much!) may just cause slight or negligible changes in time-dependent concentrations and curves. **Therefore, to make this program proceed faster, it's firstly recommended to tenfold increase the `Acc` value with other parameters unchanged.**

In the `!Solve` block, the following parameters are set. Adjusting these parameters does not change the essential results, but changes how to display results:
- `Tscale`: Converting seconds into other time units, which was set to 60 to convert seconds into minutes. (Must be greater than 0)
- `Low_limit`: The count that determines how many rows of data should be discarded from the beginning of the reaction. This setting only make impacts on the ratios of products, to avoid zero-division error. (Must be greater than 0)

### Explanations of custom functions
There are several custom functions in the `!func` block, and they are:
- `Keq(delG)`: Calculating the equilibrium constant $K^{o}$ from a given standard molar Gibbs free energy change ($\Delta G^{o}$, `delG`, unit: kcal/mol), using the isothermal equation:
$$
K^{o}=exp(-\Delta G^{o}/RT)
$$
- `kTST(bar)`: Calculating the rate constant $k^{TST}$ from a given standard molar Gibbs free energy change of activation ($\Delta G^{\ddagger}$, `bar`, unit: kcal/mol), using the transition-state theory (TST):
$$
k^{TST}=\frac{kT}{h(c^{o})^{n-1}} exp(-\Delta G^{\ddagger}/RT)
$$
- `reqs(t,u)`: Containing the concentrations of all reagents, products, and intermediates, and interpreting all defined elementary reactions into differential rate equations, which essentially describe the dynamic behavior of the studied reaction system.
- `test(t,u)`: Analogous to the `reqs(t,u)`, but it describes a much simpler reaction system, to test this program. It is unused and doesn't relate to the studied reaction system.

### Contact the author
Please feel free to contact the author if you'd like to report (including, but not limited to):
- Occurrence of unexpected errors
- Bug and error reports
- Suggestions to improve the theoretical model
- Willingness to modify this program for other uses

In addition to posting issues, you can also mail to:
ZhuZLTMSCN@outlook.com or
2013147@mail.nankai.edu.cn
