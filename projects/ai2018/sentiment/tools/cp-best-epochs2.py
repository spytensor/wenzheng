#!/usr/bin/env python 
# -*- coding: utf-8 -*-
# ==============================================================================
#          \file   find-best-epoch.py
#        \author   chenghuige  
#          \date   2018-10-07 10:32:35.416608
#   \Description  
# ==============================================================================

  
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys 
import os

import glob
import gezi

model_dir = '../' if not len(sys.argv) > 1 else sys.argv[1]

thre = 0.71 if not len(sys.argv) > 2 else float(sys.argv[2])

key = 'adjusted_f1/mean' if not len(sys.argv) > 3 else sys.argv[3]
#key = 'loss/mean' if not len(sys.argv) > 3 else sys.argv[3]

print('model_dir', model_dir, 'thre', thre, 'key', key)

if 'loss' not in key:
  print('greater is better')
  cmp = lambda x, y: x > y 
else:
  print('less is better')
  cmp = lambda x, y: x < y

# model.ckpt-3.00-9846.valid.metrics
# ckpt-4.valid.metrics 
for dir_ in glob.glob(f'{model_dir}/*/*'):
  if not os.path.isdir(dir_):
    continue
  print(dir_)
  best_score = 0 if 'loss' not in key else 1e10
  best_epoch = None
  best_iepoch = None

  in_epoch_dir = True
  files = glob.glob(f'{dir_}/epoch/*.valid.metrics')
  if not files:
    in_epoch_dir = False
    files = glob.glob(f'{dir_}/ckpt/*.valid.metrics')

  for file_ in files: 
    epoch = gezi.strip_suffix(file_, 'valid.metrics').split('-')[1]
    iepoch = int(float(epoch))
    for line in open(file_):
      name, score = line.strip().split()
      score = float(score)
      if name != key:
        continue 
      if cmp(score, best_score):
        best_score = score
        best_epoch = epoch
        best_iepoch = iepoch
  print('best_epoch:', best_epoch, 'best_score:', best_score) 
  
  if best_epoch and cmp(best_score, thre):
    if in_epoch_dir:
      command = f'ensemble-cp.py {dir_}/epoch/model.ckpt-{best_epoch}'
    else:
      command = f'ensemble-cp.py {dir_}/ckpt/ckpt-{best_epoch}'
    print(command)
    #os.system(command)
    #print(dir_)
    dir2_ = dir_.replace('temp', 'mount2/temp').replace('model.csv', 'model')
    dir3_ = dir_.replace('model.csv', 'model.ckpt')
    os.system(f'mkdir -p {dir3_}/epoch')
    os.system(f'mkdir -p {dir3_}/ckpt')

    if in_epoch_dir:
      command = f'rsync {dir2_}/epoch/model.ckpt-{best_epoch}* {dir3_}/epoch'
    else:
      command = f'rsync {dir2_}/ckpt/ckpt-{best_epoch}* {dir3_}/ckpt'

    print(command)
    os.system(command)

