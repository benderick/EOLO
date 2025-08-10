# api base=yolo11 user=benderick exp_timestamp=t23458
"""
base=yolo11,yolo11 copy,yolo11 copy 2,yolo11 copy 3,yolo11 copy 4 HEAD=AFPN4Head,AFPNHead DOWN_UP=ADown ATTENTION=EIEStem user=test mod_timestamp=t1754318068366
"""
# set working directory, get root path
import rootutils
ROOT = rootutils.setup_root(__file__, dotenv=True, pythonpath=True, cwd=True)
import hydra
from omegaconf import DictConfig, OmegaConf, ListConfig
import os
import yaml
from datetime import datetime
# -----------------------------------------------------
class CustomYAMLDumper(yaml.SafeDumper):
    """
    自定义YAML输出器，用于格式化特定的数据结构
    """
    def write_line_break(self, data=None):
        super().write_line_break(data)

    def represent_list(self, data):
        """
        自定义列表表示方法，针对特定格式进行处理
        """
        # 检查是否为网络层配置格式 [from, repeats, module, args]
        if (len(data) == 4 and 
            isinstance(data[0], (int, list)) and 
            isinstance(data[1], int) and 
            isinstance(data[2], str) and 
            isinstance(data[3], list)):
            # 使用流式风格（内联格式）
            return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
        
        # 检查是否为scales配置格式 [depth, width, max_channels]
        if (len(data) == 3 and 
            all(isinstance(x, (int, float)) for x in data)):
            # 使用流式风格（内联格式）
            return self.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
        
        # 对于其他列表，使用默认格式
        return self.represent_sequence('tag:yaml.org,2002:seq', data)

# 注册自定义列表表示方法
CustomYAMLDumper.add_representer(list, CustomYAMLDumper.represent_list)

def format_yaml_content(data):
    """
    格式化YAML内容，确保特定结构使用正确的格式
    
    Args:
        data (dict): 要格式化的数据
        
    Returns:
        str: 格式化后的YAML字符串  
    """
    # 使用自定义dumper生成YAML
    yaml_str : str = yaml.dump(
        data,
        Dumper=CustomYAMLDumper, # type: ignore
        default_flow_style=False,
        allow_unicode=True,
        indent=2,
        width=120,
        sort_keys=False
    )
    
    # 进一步优化格式 - 添加注释和美化
    lines = yaml_str.split('\n')
    formatted_lines = []
    
    in_backbone = False
    in_head = False
    in_scales = False
    
    for i, line in enumerate(lines):
        if line.strip().startswith('scales:'):
            in_scales = True
            in_backbone = False
            in_head = False
            formatted_lines.append('scales:')
            formatted_lines.append('  # [depth, width, max_channels]')
            continue
        elif line.strip().startswith('backbone:'):
            in_backbone = True
            in_head = False
            in_scales = False
            formatted_lines.append('')  # 添加空行
            formatted_lines.append('backbone:')
            formatted_lines.append('  # [from, repeats, module, args]')
            continue
        elif line.strip().startswith('head:'):
            in_head = True
            in_backbone = False
            in_scales = False
            formatted_lines.append('')  # 添加空行
            formatted_lines.append('head:')
            continue
        elif line.strip() and not line.startswith(' ') and not line.strip().startswith('- ['):
            in_backbone = False
            in_head = False
            in_scales = False
        
        # 处理scales部分的缩进
        if in_scales and line.strip() and ':' in line and not line.startswith('  '):
            # 为scales的子项添加正确缩进
            line = '  ' + line.strip()
        
        # 处理backbone和head的缩进 - 简化逻辑
        if (in_backbone or in_head) and line.strip().startswith('- ['):
            # 确保第一级子项有4个空格的缩进
            line = '  ' + line.strip()
        
        formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def oc_to_dict(omf: DictConfig) -> dict:
    return OmegaConf.to_container(omf, resolve=True) # type: ignore

def process_model(cfg: DictConfig) -> DictConfig:
    # 添加Attention相关逻辑
    if cfg.template.ATTENTION:
        cfg.template.backbone.append([-1, 1, cfg.template.ATTENTION, []])
        for layer in cfg.template.head:
            arg0 = layer[0]
            if isinstance(arg0, int) and arg0 >= 10:
                layer[0] = layer[0] + 1 # type: ignore
            if isinstance(arg0, ListConfig) and len(arg0) > 0:
                for i,v in enumerate(arg0):
                    if isinstance(v, int) and v >= 10:
                        arg0[i] = v + 1 # type: ignore

    # 其他处理逻辑...
    
    return cfg
# -----------------

@hydra.main(version_base="1.3", config_path="../configs", config_name="create")
def main(cfg: DictConfig) -> None:
    used_keys = set(cfg.template.keys())-set(["name", "nc", "scales", "backbone", "head"])
    model_name = cfg.template.name + "-" + "-".join([cfg.template.get(key) for key in used_keys if cfg.template.get(key)])
    print(f"   📝 Model name: {model_name}")
    # 筛选逻辑 --------------------------
    if ("4Head" in cfg.template.name) ^ ("4Head" in cfg.template.HEAD):
        print(f"   ⚠️ 模版检测头与选择的检测头不一致，略过。")
        return
    if ("attn" in cfg.template.name) ^ (cfg.template.ATTENTION is not None):
        print(f"   ⚠️ 模版与选择的Attention不一致，略过。")
        return
    # ---------------------------------
    cfg.template.name = model_name
    # 处理逻辑，如是否添加Attention，参数等------
    # cfg = process_model(cfg)
    # ---------------------------------
    USER_GENERATE_DIR = ROOT / "configs" / "model" \
                        / cfg.user / "generate" / f"{cfg.time}{'-' + cfg.run_name if cfg.run_name != 'create' else ''}"
    if not os.path.exists(USER_GENERATE_DIR):
        os.makedirs(USER_GENERATE_DIR)
        
    yaml_path = USER_GENERATE_DIR / f"{model_name}.yaml"

    model = oc_to_dict(cfg.template)
    
    # 创建YAML文件头注释
    header_comment = f"""# 自动生成的模型配置文件
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 用户: {cfg.user}
# 模板: {cfg.template.name}
# 模型名称: {model_name}
# 
# 配置参数:
#   - 下采样模块: {cfg.template.DOWNSAMPLE}
#   - 卷积模块: {cfg.template.CONVOLUTION}  
#   - 融合模块: {cfg.template.FUSION}
#   - 检测头: {cfg.template.HEAD}
"""
    
    # 使用自定义格式化方法
    formatted_yaml = format_yaml_content(model)
    
    # 写入文件
    with open(yaml_path, 'w', encoding='utf-8') as f:
        f.write(header_comment)
        f.write(formatted_yaml)
    
    print(f"   ✅ 模型创建成功: {yaml_path}")

if __name__ == "__main__":
    main()