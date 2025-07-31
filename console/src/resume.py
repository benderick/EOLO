from ultralytics import YOLO
model = YOLO("/home/zhangSHUO/zhangshuo/YOLO-UAV/logs/YOLO-UAV/multiruns/2025-05-29_22-54-03/0-MBFD/YOLO-UAV/MBFD/weights/last.pt")
model.model_dict_str = ""
model.train(resume=True)
