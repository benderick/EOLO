import warnings
warnings.filterwarnings('ignore')
from ultralytics import YOLO

if __name__ == '__main__':
    """
    快速验证 YOLO 模型是否有错误的脚本
    
    验证方法包括:
    1. 模型加载测试 - 检查配置文件是否正确
    2. 模型信息检查 - 验证模型结构
    3. 性能分析测试 - 检查前向传播和计算图
    4. 模型融合测试 - 验证模型优化能力
    
    这些测试可以在不进行完整训练的情况下发现大部分模型错误
    """
    
    # 选择要验证的模型配置文件
    model_path = '/icislab/volume3/benderick/futurama/EOLO/configs/model/common/comparison/RFD.yaml'
    imgsz = [640, 640]
    
    print(f"🔍 验证 YOLO 模型: {model_path}")
    print("=" * 60)
    
    try:
        # 1. 模型加载测试
        print("📁 1. 模型加载测试...")
        model = YOLO(model_path)
        print("   ✅ 模型加载成功")
        
        # 2. 模型信息检查
        print("\n📊 2. 模型信息检查...")
        model.info(detailed=False)
        print("   ✅ 模型信息正常")
        
        # 3. 性能分析测试（最重要的验证）
        print(f"\n⚡ 3. 性能分析测试 (图像尺寸: {imgsz})...")
        try:
            model.profile(imgsz=imgsz)
            print("   ✅ 性能分析通过 - 前向传播正常")
        except Exception as e:
            print(f"   ❌ 性能分析失败: {e}")
            raise e
        
        # 4. 模型融合测试
        print("\n🔗 4. 模型融合测试...")
        try:
            model.fuse()
            print("   ✅ 模型融合成功")
        except Exception as e:
            print(f"   ⚠️ 模型融合失败: {e}")
            print("   ℹ️ 融合失败不影响训练，但可能影响推理性能")
        
        # 验证总结
        print("\n" + "=" * 60)
        print("🎉 模型验证通过!")
        print("✅ 模型配置正确，可以用于训练")
        print("✅ 前向传播正常")
        print("✅ 计算图构建成功")
        
    except Exception as e:
        print(f"\n❌ 模型验证失败: {e}")
        print("\n💡 常见问题和解决方案:")
        print("   • 配置文件语法错误 → 检查 YAML 文件格式")
        print("   • 模块导入错误 → 检查自定义模块路径")
        print("   • 网络结构错误 → 检查层的输入输出维度匹配")
        print("   • 依赖缺失 → 检查所需的 Python 包是否安装")
        
        # 详细错误信息
        print(f"\n🔍 详细错误信息:")
        import traceback
        traceback.print_exc()
        
        exit(1)