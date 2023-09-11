[![Build Status](https://travis-ci.com/hongdavid94/ancestry.svg?branch=main)](https://travis-ci.com/hongdavid94/ancestry)
[![Coverage Status](https://coveralls.io/repos/github/hongdavid94/ancestry/badge.svg?branch=main)](https://coveralls.io/github/hongdavid94/ancestry?branch=main)

# ancestry-informative SNP scAI-SNP

## installation

Because this repository includes large files (over 100MB), you may use [git-lfs](https://git-lfs.com/) to install these large files in the repository. Here is the link that can direct you to the installation [instructions](https://github.com/git-lfs/git-lfs?utm_source=gitlfs_site&utm_medium=installation_link&utm_campaign=gitlfs#installing). Here are some helpful instructions.

### Step 0: Make sure you have the prerequisites 
- pip
- python 3.7+

### Step 1: installation of scAI-SNP

```{bash}
git clone https://github.com/hongdavid94/scAI_SNP.git
cd scAI_SNP
pip install .
```

### Step 2A (you may instead do Step 2B): installation of git-lfs

1. install the appropriate binary package in this [list](https://github.com/git-lfs/git-lfs/releases) under "Assets"
2. untar the file and move the folder to an appropriate path of your choice
3. if you don't have write access or do not prefer that the executable file be automatically installed under your directory /usr/bin, modify the install.sh file by changing its prefix to a directory of your choice (make sure this directory is on your $PATH). If you don't any issue with the installation at /usr/bin, skip this step
4. run the installation by command `./install.sh`
5. go to the directory where you have cloned the repository
6. use command `git lfs install` to apply git-lfs to the repository
7. use command `git lfs ls-files` to make sure the large files of the repository are listed in the terminal output
8. use command `git lfs pull` to convert git-lfs tagged files to their full size (this will download about ~1.2GB of memory)

### Step 2B (instead of following Step 2A): download large files using dropbox links

Use the following dropbox link to download the large files needed for the package [link](https://www.dropbox.com/sh/t8asohtbg6y8y8i/AABgztiVy4LlZ5DEwR4UZLi_a?dl=0). Anyone with the link can download the files. Make sure all the files are located probably such that
data/ and model/ files are in your scAI_SNP folder

## running the classification

### Command Line Interface
```{bash}
scAI_SNP_classify <input_genotype_file> --name_input <input_name_file> --bool_save_plot <True or False>
```
### File Format
#### <input_genotype_file>
`input_genotype_file` must be a tab-separated text file of exactly 4.5 million (4,586,890 genotypes) rows which would correspond, in order, to the genotypes of 4.5 million SNPs [here](https://www.dropbox.com/scl/fi/65sn4qinedwsd6sh6eu4f/snp_meta_4.5M.col?rlkey=ncscgtr4p65ll46itn9fjkvy9&dl=0) of your input. There **must be no header row** and you may have multiple columns of the data in which multiple columns correspond to multiple samples. Each entry of the genotype must be `{NA, 0, 0.5, 1}`, which represents missing genotype, homozygous reference, heterozygous mutation, and homozygous mutation genotype. 

For example, for these three SNPs listed, '1:13649:G:C', '1:13868:A:G', and '1:14464:A:T', correspond to SNPs at chromosome 1 at position 13649, 13868, and 14464, respectively (using the Human genome reference GRCh38 or hg38). For a sample, if the read of the first SNP is G/G, then the genotype would be homozygous reference because both match the reference and its corresponding data value would be 0. For the second SNP, if the observed genotype is A/G, then the corresponding data value would be 0.5. And if the genotype of the third SNP is not obtainable, then the corresponding data value must be `'NA'`. To reiterate, all data values in `input_genotype_file` must be `{NA, 0, 0.5, 1}` with allowing exceptions of `{Na, na, NaN, nan}` as `NA`, `{-0, 0.0, -0.0}` as `0`, `{1.0}` as `1`.

#### <input_name_file>
`input_name_file` is an optional parameter and a text file in which you can specify the name of the sample. For each column of `input_genotype_file`, from left to right, you can write down the sample name for each row. If the number of rows in `input_name_file` and the number of columns in `input_genotype_file` do not match, this parameter will be ignored and a default naming will be given. The default name would be the file name of `input_genotype_file` followed by `_#` where `#` will range from 1 to the number of samples (columns in `input_genotype_file`).

