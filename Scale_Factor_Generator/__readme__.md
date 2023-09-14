### How to use the Scale_Generator.py?
1. `Python 3` is required. Then, make sure package `Scipy` is installed (Versions later than 1.8.1 are recommended). If not, you can use `pip` to download it in the terminal.
2. Download the `Scale_Generator.py` and choose an rar file`*__output_XX.rar` with Gaussian16 output files `*.log` from test sets. QC method and basis sets are labelled, and the number at the end of filename is the amount of molecules in test sets.
3. Extract the downloaded rar file in a directory with `Scale_Generator.py`.
4. Run `Scale_Generator.py`, and a `scaleRes.out` file will be generated. The calculated harmonic frequency scale factors are at the end of the `scaleRes.out`. If error occurs from `scipy.minimize`, please modify the value of `guess` and rerun.
Note: Temporarily, this program only support output files (__`*.log`__) from `Gaussian`. Other QC softwares are not supported.

### What are the principles behind the frequency scale factors?
Simply put, under most circumstances, in quantum chemistry computation softwares, **harmonic** frequencies are output after a frequency analysis. 

However, for a certain normal mode, the calculated harmonic frequency is often higher than the experimentally-obtained frequency, making errors to the calculation of thermodynamic properties. An a posteriori method is adopted: multiply all calculated harmonic frequencies with a **scale factor**, to minimize the errors arising from the difference between harmonic frequencies and experimental frequencies. (Note: Anharmonic frequency calculation is available but much more costly in most mainstream QC softwares.)

To determine the optimal value of scale factors for a certain level of computation (e.g. B3LYP/6-31G*, M06-2X/def2-SVP), a test set need establishing, in which many small molecules have their experimentally-confirmed frequencies. Thereafter, at the chosen level of computation, construct and perform geometry optimization & frequency analysis to each molecule in the test set. Having obtained both calculated and experimental frequencies, an error function (e.g. variance) about the scale factor can be established. Usually, the final scale factor equals the minimum point of the error function.

To see how `Scale_Generator.py` works, you can also check the Supporting Information (page S-42 ~ S-45) of the following paper:
https://doi.org/10.1039%2FD3GC00344B

If you want to learn more about the scale factor, I recommend you to read this document (by Merrick *et. al.*, 2006):
https://pubs.acs.org/doi/10.1021/jp073974n
### Last but not the least, if you have any other problems, please feel free to post an issue!
