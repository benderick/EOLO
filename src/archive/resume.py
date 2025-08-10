from ultralytics import YOLO
model = YOLO("/icislab/volume3/benderick/futurama/EOLO/logs/benderick/multiruns/2025-08-01_16-17-31/0-yolo/benderick/yolo/weights/last.pt")
# model.model_dict_str = ""
model.train(resume=True)
