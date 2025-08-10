#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO 模型快速验证工具
在不进行完整训练的情况下验证模型是否正确
"""

import warnings
warnings.filterwarnings('ignore')




from ultralytics import YOLO

a = YOLO("/icislab/volume3/benderick/futurama/EOLO/configs/model/paper/yolo11.yaml")