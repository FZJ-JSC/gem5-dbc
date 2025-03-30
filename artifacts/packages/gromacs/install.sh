#!/bin/bash

# PKG
PKG_NAME="gromacs"
PKG_VER="v2024.5"
PKG_GIT="https://gitlab.com/gromacs/gromacs.git"

git -C $SRCDIR clone --depth 1 --branch $PKG_VER $PKG_GIT

for P in *.patch; do
    patch -d $SRCDIR/$PKG_NAME -p1 < $P
done

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_INSTALL_PREFIX="$BENCHD/$PKG_NAME" -DGMX_USE_M5:BOOL=ON -DBUILD_TESTING:BOOL=OFF -DGMX_INSTALL_NBLIB_API:BOOL=OFF -DBUILD_SHARED_LIBS:BOOL=OFF -DGMXAPI:BOOL=OFF -DGMX_THREAD_MPI:BOOL=OFF -DGMX_BUILD_OWN_FFTW=ON

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/bin/gmx_m5

cmake -B $BLDDIR/$PKG_NAME $SRCDIR/$PKG_NAME -DCMAKE_INSTALL_PREFIX="$BENCHD/$PKG_NAME" -DGMX_USE_M5:BOOL=OFF -DBUILD_TESTING:BOOL=OFF -DGMX_INSTALL_NBLIB_API:BOOL=OFF -DBUILD_SHARED_LIBS:BOOL=OFF -DGMXAPI:BOOL=OFF -DGMX_THREAD_MPI:BOOL=OFF -DGMX_BUILD_OWN_FFTW=ON 

make  -C $BLDDIR/$PKG_NAME -j$(nproc)

install -D -m 0755 -t $BENCHD/$PKG_NAME/bin $BLDDIR/$PKG_NAME/bin/gmx

mkdir -p $BENCHD/$PKG_NAME/data

# MPI Input files for GROMACS performance evaluations
BASE_URL="https://www.mpinat.mpg.de"
DATA_FILES=(
    "3925268/cmet_eq.zip"
    "3925279/cmet_ti.zip"
    "3925290/hif2a_eq.zip"
    "3925301/hif2a_ti.zip"
    "3925312/ligand_cmet_eq.zip"
    "3925323/ligand_cmet_ti.zip"
    "3925334/shp2_eq.zip"
    "3925345/shp2_ti.zip"
    "632216/benchBFC.zip"
    "632219/benchBFI.zip"
    "632222/benchBNC.zip"
    "632214/benchBNI.zip"
    "632223/benchBTC.zip"
    "632215/benchBTI.zip"
    "632218/benchSFC.zip"
    "632220/benchSFI.zip"
    "632213/benchSNC.zip"
    "632217/benchSNI.zip"
    "632221/benchSTC.zip"
    "632212/benchSTI.zip"
)

wget $BASE_URL/benchMEM -O benchMEM.zip

for item in "${DATA_FILES[@]}"; do
    wget $BASE_URL/$item;
done

for i in *.zip; do
    unzip $i -d $BENCHD/$PKG_NAME/data ;
done
