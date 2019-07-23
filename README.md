[![Build Status](https://travis-ci.com/anenriquez/mrta_temporal_models.svg?token=QudZDF4JraaUN8o4yWNo&branch=master)](https://travis-ci.com/anenriquez/mrta_temporal_models)

# Temporal Models for MRTA (multi-robot task allocation)

Get the requirements:
```
pip3 install -r requirements.txt
```

Add the task_allocation to your `PYTHONPATH` by running:

```
sudo pip3 install -e .
```



## References

#### Static Robust Execution Algorithm (SREA) 

Lund et al. 2017. Robust Execution of Probabilistic Temporal Plans. In Proc. of the 31th Lund et al. 2017. Robust Execution of Probabilistic Temporal Plans. In Proc. of the 31th Conference on Artificial Intelligence (AAAI. 2017)
Paper available [here](https://www.cs.hmc.edu/HEAT/papers/Lund_et_al_AAAI_2017.pdf).


Abrahams et al. 2019. DREAM: An Algorithm for Mitigating the Overhead of Robust Rescheduling. In Proc. of the 29th International Conference on Automated Planning and Scheduling (ICAPS-2019). Paper available [here](https://www.cs.hmc.edu/HEAT/papers/Abrahams_et_al_ICAPS_2019.pdf).

#### Degree of Strong Controllability (DSC)

Akmal et al. 2019. Quantifying Degrees of Controllability for Temporal Networks with Uncertainty. In Proc of the 29th International Conference on Automated Planning and Scheduling (ICAPS-2019). Paper available [here](https://www.cs.hmc.edu/HEAT/papers/Akmal_et_al_ICAPS_2019.pdf)

## Acknowledgements

- The SREA code is based on [this](https://github.com/HEATlab/DREAM) repository of [HEATlab](https://www.cs.hmc.edu/HEAT/).

MIT License

Copyright (c) 2019 HEATlab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


- The DSC code in based on [this](https://github.com/HEATlab/Prob-in-Ctrl/) repository of [HEATlab](https://www.cs.hmc.edu/HEAT/).

MIT License

Copyright (c) 2019 HEATlab

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
