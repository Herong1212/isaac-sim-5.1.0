#!/bin/bash

# DO NOT MODIFY

set -e
ROOT_DIR=$(realpath $(dirname ${BASH_SOURCE}))
EXTS_DIR=$ROOT_DIR/exts
echo
echo "MPI and UCX root: " $EXTS_DIR
echo

export RTX_MPI_DIR=$EXTS_DIR/omni.mpi.libs/ompi
export RTX_UCX_DIR=$EXTS_DIR/omni.ucx.libs/bin
export OPAL_PREFIX=$RTX_MPI_DIR
export OMPI_HOME=$RTX_MPI_DIR
export MPI_HOME=$RTX_MPI_DIR
export PATH=$RTX_MPI_DIR/bin:$PATH
export LD_LIBRARY_PATH=$RTX_MPI_DIR/lib:$RTX_UCX_DIR:$$RTX_UCX_DIR/ucx:$LD_LIBRARY_PATH
export UCX_LOG_LEVEL=info

if [ -n "${TEAMCITY_VERSION}" ]; then
    echo "Teamcity version " $TEAMCITY_VERSION
    # Allows using mpirun without ssh
    export OMPI_MCA_plm_rsh_agent=
fi

mpirun "$@"
