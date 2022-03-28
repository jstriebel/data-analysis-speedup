# Declarative Configs for Maintainable Reproducible Code

<img src="https://2022.pycon.de/static/media/PyConDE_PyDataBer_circle_trans_500.png" width="150" height="150">

Material for my talk at the [PyConDE & PyData Berlin 2022](https://2022.pycon.de/program/VYS8XY/):

## Description

Your data analysis pipeline works. ***Nice.***<br/>
Could it be faster? ***Probably.***<br/>
Do you need to parallelize? ***Not yet.***

We'll go through optimization steps that **boost the performance of your data analysis pipeline on a single core**, reducing time & costs. This walkthrough shows tools and strategies to identify and mitigate bottlenecks, and demonstrate them in an example. The 5 steps cover:

* Identifying bottlenecks: profiling memory, IO & cpu
* Efficient IO
* Memory optimizations
* Vector-optimizations
* Jit-ing using numba

This talk is suited for data scientists on a beginner and intermediate level, typically working with a numpy/scipy/… stack or similar. The talk gives strategies & concrete suggestions how to speed up an existing analysis pipeline, which is demonstrated practically on an example, showing the gained speed & memory improvements of each step.
