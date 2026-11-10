#!/bin/bash
# the VHDL writer must run on the GT menus and give the same output regardless of python's hash seed
for menu in step1_2024 v0p0_2026; do
  for seed in 1 2; do
    mkdir -p ${menu}_${seed}
    PYTHONHASHSEED=${seed} python3 "${SCRAM_TEST_PATH}"/test_algounitwriter.py -n 4 -o ${menu}_${seed} \
      -i L1Trigger.Configuration.Phase2GTMenus.SeedDefinitions.${menu}.l1tGTMenu_cff > ${menu}_${seed}.log || exit $?
  done
  for slr in 0 1 2 3; do
    [ -s ${menu}_1/p2gt_algos_slr${slr}.vhd ] || { echo "${menu}: p2gt_algos_slr${slr}.vhd not written"; exit 1; }
  done
  diff -r ${menu}_1 ${menu}_2 || { echo "${menu}: output depends on the hash seed"; exit 1; }
  echo "${menu}: OK"
done
