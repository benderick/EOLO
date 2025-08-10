#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO 模型快速验证工具
在不进行完整训练的情况下验证模型是否正确
"""

import warnings
warnings.filterwarnings('ignore')

import torch
import time
import traceback
import sys
from pathlib import Path
from typing import Optional, Any
from ultralytics import YOLO

class YOLOModelValidator:
    """YOLO 模型验证器"""
    
    def __init__(self, model_path: str, imgsz: list = [640, 640], device: str = 'cpu'):
        """
        初始化验证器
        
        Args:
            model_path: 模型配置文件路径
            imgsz: 输入图像尺寸
            device: 运行设备
        """
        self.model_path = model_path
        self.imgsz = imgsz
        self.device = device
        self.model: Optional[YOLO] = None
        self.validation_results = {
            'model_path': model_path,
            'tests': {},
            'overall_status': 'UNKNOWN',
            'errors': [],
            'warnings': []
        }
        
        # 尝试加载模型
        self.load_model()
    
    def load_model(self):
        """加载 YOLO 模型"""
        try:
            print(f"🔄 加载模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            print("✅ 模型加载成功")
            
        except Exception as e:
            error_msg = f"❌ 模型加载失败: {str(e)}"
            print(error_msg)
            self.validation_results['errors'].append(error_msg)
            traceback.print_exc()
    
    def log_test_result(self, test_name: str, status: str, message: str, **kwargs):
        """记录测试结果"""
        result = {
            'status': status,
            'message': message,
            'timestamp': time.time(),
            **kwargs
        }
        self.validation_results['tests'][test_name] = result
        
        # 打印结果
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌', 
            'WARNING': '⚠️',
            'SKIP': '⏭️'
        }
        print(f"{status_emoji.get(status, '❓')} {test_name}: {message}")
    
    def test_model_info(self):
        """测试 1: 模型信息检查"""
        print("\n📊 1. 模型信息检查...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            # 获取模型信息
            info_output = self.model.info(detailed=False, verbose=False)
            self.log_test_result('model_info', 'PASS', "模型信息获取成功")
            return True
            
        except Exception as e:
            self.log_test_result(
                'model_info', 'FAIL',
                f"模型信息获取失败: {str(e)}"
            )
            return False
    
    def test_model_parameters(self):
        """测试 2: 模型参数检查"""
        print("\n🔍 2. 模型参数检查...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            if hasattr(self.model, 'model') and self.model.model is None:
                raise Exception("模型结构未正确初始化")
            
            # 获取参数统计
            if hasattr(self.model, 'model') and hasattr(self.model.model, 'parameters'):
                param_count = sum(p.numel() for p in self.model.model.parameters())
                trainable_count = sum(p.numel() for p in self.model.model.parameters() if p.requires_grad)
                
                self.log_test_result(
                    'parameters', 'PASS',
                    f"总参数: {param_count:,}, 可训练: {trainable_count:,}",
                    total_params=param_count,
                    trainable_params=trainable_count
                )
            else:
                self.log_test_result(
                    'parameters', 'SKIP',
                    "无法访问模型参数信息"
                )
            
            return True
            
        except Exception as e:
            self.log_test_result(
                'parameters', 'FAIL',
                f"参数检查失败: {str(e)}"
            )
            return False
    
    def test_device_compatibility(self):
        """测试 3: 设备兼容性检查"""
        print("\n🖥️ 3. 设备兼容性检查...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            # 检查设备可用性
            if self.device == 'cuda':
                if not torch.cuda.is_available():
                    self.log_test_result(
                        'device_compatibility', 'WARNING',
                        "CUDA 不可用，将使用 CPU"
                    )
                    self.device = 'cpu'
                    return True
                else:
                    # 移动模型到 GPU
                    if hasattr(self.model, 'model') and hasattr(self.model.model, 'cuda'):
                        self.model.model = self.model.model.cuda()
            
            self.log_test_result(
                'device_compatibility', 'PASS',
                f"设备 {self.device} 兼容性检查通过"
            )
            return True
            
        except Exception as e:
            self.log_test_result(
                'device_compatibility', 'FAIL',
                f"设备兼容性检查失败: {str(e)}"
            )
            return False
    
    def test_forward_pass(self):
        """测试 4: 前向传播"""
        print("\n🔮 4. 前向传播测试...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            # 创建测试输入 (使用正确的数据范围 [0,1])
            test_input = torch.rand(2, 3, self.imgsz[0], self.imgsz[1])
            
            if self.device == 'cuda' and torch.cuda.is_available():
                test_input = test_input.cuda()
            elif self.device == 'cpu':
                test_input = test_input.cpu()
            
            results = {}
            
            # 测试1: 使用底层 PyTorch 模型进行推理
            if hasattr(self.model, 'model') and hasattr(self.model.model, 'eval'):
                self.model.model.eval()
                with torch.no_grad():
                    if callable(self.model.model):
                        outputs_raw = self.model.model(test_input)
                        results['raw_model'] = f"原始模型输出类型: {type(outputs_raw)}"
                        if isinstance(outputs_raw, (list, tuple)):
                            results['raw_model'] += f", 输出数量: {len(outputs_raw)}"
                            if len(outputs_raw) > 0 and hasattr(outputs_raw[0], 'shape'):
                                results['raw_model'] += f", 第一个输出形状: {outputs_raw[0].shape}"
            
            # 测试2: 使用 YOLO 预测接口
            try:
                outputs_predict = self.model.predict(test_input, verbose=False)
                results['predict_api'] = f"预测API输出类型: {type(outputs_predict)}"
                if isinstance(outputs_predict, (list, tuple)) and len(outputs_predict) > 0:
                    results['predict_api'] += f", 结果数量: {len(outputs_predict)}"
            except Exception as e:
                results['predict_api'] = f"预测API失败: {str(e)}"
            
            # 记录测试结果
            if results:
                result_summary = " | ".join(results.values())
                self.log_test_result(
                    'forward_pass', 'PASS',
                    f"前向传播测试通过 - {result_summary}"
                )
                return True
            else:
                raise Exception("所有前向传播方式都失败")
                
        except Exception as e:
            self.log_test_result(
                'forward_pass', 'FAIL',
                f"前向传播失败: {str(e)}"
            )
            return False
    
    def test_model_fuse(self):
        """测试 6: 模型融合"""
        print("\n🔗 6. 模型融合测试...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            if hasattr(self.model, 'fuse'):
                self.model.fuse()
                self.log_test_result('model_fuse', 'PASS', "模型融合成功")
            else:
                self.log_test_result('model_fuse', 'SKIP', "模型不支持融合操作")
            return True
            
        except Exception as e:
            self.log_test_result(
                'model_fuse', 'WARNING',
                f"模型融合失败: {str(e)}"
            )
            return False
    
    def test_gradient_computation(self):
        """测试 5: 梯度计算（反向传播）"""
        print("\n📈 5. 梯度计算测试...")
        try:
            # 检查模型是否已加载
            if self.model is None:
                raise Exception("模型未正确加载")
            
            # 检查是否可以访问底层模型
            if not (hasattr(self.model, 'model') and hasattr(self.model.model, 'parameters')):
                self.log_test_result(
                    'gradient_computation', 'SKIP',
                    "无法访问模型参数，跳过梯度测试"
                )
                return True
            
            # 保存原始状态
            original_training_mode = self.model.model.training
            
            # 确保模型在正确的设备上
            if self.device == 'cuda' and torch.cuda.is_available():
                self.model.model = self.model.model.cuda()
            elif self.device == 'cpu':
                self.model.model = self.model.model.cpu()
            
            # 确保所有参数都需要梯度
            for param in self.model.model.parameters():
                param.requires_grad_(True)
            
            # 设置为训练模式
            self.model.model.train()
            
            # 清零所有梯度
            for param in self.model.model.parameters():
                if param.grad is not None:
                    param.grad.zero_()
            
            # 创建需要梯度的输入，确保在正确的设备上
            test_input = torch.randn(2, 3, self.imgsz[0], self.imgsz[1], requires_grad=True)
            
            if self.device == 'cuda' and torch.cuda.is_available():
                test_input = test_input.cuda()
            else:
                test_input = test_input.cpu()
            
            # 前向传播
            outputs = self.model.model(test_input)
            
            # 计算损失并反向传播
            try:
                # 根据诊断结果，YOLO模型在训练模式下输出是list
                if isinstance(outputs, (list, tuple)) and len(outputs) > 0:
                    # 选择第一个输出计算损失
                    loss = outputs[0].sum()
                elif hasattr(outputs, 'sum'):
                    loss = outputs.sum()
                else:
                    raise Exception(f"不支持的输出类型: {type(outputs)}")
                
                # 确保损失需要梯度
                if not loss.requires_grad:
                    self.log_test_result(
                        'gradient_computation', 'WARNING',
                        "计算出的损失不需要梯度"
                    )
                    return False
                
                # 反向传播
                loss.backward()
                
                # 检查梯度
                param_with_grad = 0
                total_params = 0
                grad_norms = []
                significant_grads = 0  # 有意义的梯度数量
                
                for param in self.model.model.parameters():
                    if param.requires_grad:
                        total_params += 1
                        if param.grad is not None:
                            param_with_grad += 1
                            grad_norm = param.grad.norm().item()
                            if grad_norm > 1e-8:  # 只计算有意义的梯度
                                significant_grads += 1
                                grad_norms.append(grad_norm)
                
                # 恢复原始训练模式
                self.model.model.train(original_training_mode)
                
                if significant_grads > 0:  # 修改判断条件
                    avg_grad_norm = sum(grad_norms) / len(grad_norms) if grad_norms else 0
                    self.log_test_result(
                        'gradient_computation', 'PASS',
                        f"梯度计算成功 - {significant_grads}/{total_params} 个参数有有效梯度, 平均梯度范数: {avg_grad_norm:.6f}",
                        params_with_grad=significant_grads,
                        total_trainable_params=total_params,
                        avg_grad_norm=avg_grad_norm
                    )
                    return True
                else:
                    self.log_test_result(
                        'gradient_computation', 'FAIL',
                        f"没有参数计算出有效梯度 - 总参数:{total_params}, 有梯度:{param_with_grad}, 有效梯度:{significant_grads}"
                    )
                    return False
                    
            except Exception as loss_error:
                # 恢复原始训练模式
                self.model.model.train(original_training_mode)
                self.log_test_result(
                    'gradient_computation', 'FAIL',
                    f"损失计算或反向传播失败: {str(loss_error)}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                'gradient_computation', 'FAIL',
                f"梯度计算失败: {str(e)}"
            )
            return False
    
    def test_memory_usage(self):
        """测试 7: 内存使用检查"""
        print("\n💾 7. 内存使用检查...")
        try:
            if torch.cuda.is_available() and self.device == 'cuda':
                torch.cuda.empty_cache()
                torch.cuda.reset_peak_memory_stats()
                
                # 创建测试输入
                test_input = torch.randn(2, 3, self.imgsz[0], self.imgsz[1]).cuda()
                
                # 确保模型在 GPU 上
                if hasattr(self.model, 'model') and hasattr(self.model.model, 'parameters'):
                    if not next(self.model.model.parameters()).is_cuda:
                        if hasattr(self.model.model, 'cuda'):
                            self.model.model = self.model.model.cuda()
                
                # 进行前向传播
                with torch.no_grad():
                    if hasattr(self.model, 'model') and callable(self.model.model):
                        outputs = self.model.model(test_input)
                    else:
                        outputs = self.model.predict(test_input, verbose=False)
                
                peak_memory = torch.cuda.max_memory_allocated()
                memory_mb = peak_memory / 1024 / 1024
                
                self.log_test_result(
                    'memory_check', 'PASS',
                    f"GPU 内存使用: {memory_mb:.2f} MB",
                    memory_usage_mb=memory_mb
                )
                return True
            else:
                self.log_test_result(
                    'memory_check', 'SKIP',
                    "GPU 不可用或未指定，跳过 GPU 内存检查"
                )
                return True
                
        except Exception as e:
            self.log_test_result(
                'memory_check', 'WARNING',
                f"内存检查失败: {str(e)}"
            )
            return False
    
    def run_validation(self):
        """运行所有验证测试"""
        print("🚀 开始 YOLO 模型验证...")
        print(f"模型路径: {self.model_path}")
        print(f"设备: {self.device}")
        print(f"图像尺寸: {self.imgsz}")
        print("=" * 60)
        
        # 如果模型加载失败，跳过所有测试
        if self.model is None:
            print("❌ 模型未加载，跳过所有测试")
            self.validation_results['overall_status'] = 'FAIL'
            return self.validation_results
        
        # 定义测试列表（将梯度计算测试放在模型融合之前）
        tests = [
            self.test_model_info,
            self.test_model_parameters,
            self.test_device_compatibility,
            self.test_forward_pass,
            self.test_gradient_computation,  # 在模型融合之前测试梯度
            self.test_model_fuse,           # 模型融合可能会影响梯度计算
            self.test_memory_usage,
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        # 运行测试
        start_time = time.time()
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
                else:
                    failed_tests += 1
            except Exception as e:
                print(f"❌ 测试 {test.__name__} 发生异常: {str(e)}")
                failed_tests += 1
        
        total_time = time.time() - start_time
        
        # 生成总结
        print("\n" + "=" * 60)
        print("📊 验证结果总结:")
        print(f"✅ 通过测试: {passed_tests}")
        print(f"❌ 失败测试: {failed_tests}")
        print(f"⏱️ 总耗时: {total_time:.2f} 秒")
        
        # 设置总体状态
        if failed_tests == 0:
            self.validation_results['overall_status'] = 'PASS'
            print("🎉 所有测试通过！模型验证成功")
        elif passed_tests > failed_tests:
            self.validation_results['overall_status'] = 'PARTIAL'
            print("⚠️ 部分测试通过，模型可能存在一些问题")
        else:
            self.validation_results['overall_status'] = 'FAIL'
            print("❌ 多数测试失败，模型存在严重问题")
        
        self.validation_results['summary'] = {
            'passed': passed_tests,
            'failed': failed_tests,
            'total_time': total_time
        }
        
        return self.validation_results


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='YOLO 模型验证工具')
    parser.add_argument('model_path', help='模型文件路径')
    parser.add_argument('--device', default='cuda', choices=['cpu', 'cuda'], help='运行设备')
    parser.add_argument('--imgsz', nargs=2, type=int, default=[640, 640], help='输入图像尺寸')
    
    args = parser.parse_args()
    
    # 检查模型文件是否存在
    if not Path(args.model_path).exists():
        print(f"❌ 错误: 模型文件不存在: {args.model_path}")
        sys.exit(1)
    
    # 创建验证器并运行验证
    validator = YOLOModelValidator(
        model_path=args.model_path,
        device=args.device,
        imgsz=args.imgsz
    )
    
    results = validator.run_validation()
    
    # 根据结果设置退出码
    if results['overall_status'] == 'PASS':
        sys.exit(0)
    elif results['overall_status'] == 'PARTIAL':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
