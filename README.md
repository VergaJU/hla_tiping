# hla_tiping


Easy script to run HLA typing tools on a batch of BAM files
- [arcasHLA](https://github.com/RabadanLab/arcasHLA)
 - Specifically [this fork](https://github.com/VergaJU/arcasHLA) that fixed some issues with the container and reference
- [OptiType](https://github.com/FRED-2/OptiType)
- [T1K](https://github.com/mourisl/T1K)


## Requirements

`docker` and `docker compose` are reqired to run the tools


## Usage:

clone the repository

```
git clone https://github.com/VergaJU/hla_tiping.git
```

create `data` directory:

```
cd hla_typing
mkdir data
```

copy the `BAM` files into `data`

run `./hla_typing.sh`:

```
Run HLA typining with arcasHLA, OptiTyie and T1K.

Syntax: scriptTemplate [-i|t|h|]
options:
t     number of threads. Default: 8
o     output directory. Default: hla_typing_out
s     single or paired end. Default: single
h     Print this Help.
```
