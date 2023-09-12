model_path = "./efformer.pt"

from statistics import mode
from matplotlib.pyplot import pause
from sympy import true
import torch
import torchstat
import torchvision

"""
Stas FLOPs and parameters of model.
"""

model = torchvision.models.resnet18()
# model = torch.jit.load(model_path)
model.eval()
torchstat.stat(model, (3, 224, 224))

# ######################################################################################
# print("\n###########################################################################\n")

# import torch
# import torchvision
# from torchsummary import summary

# model = torchvision.models.resnet18()
# # model = torch.jit.load(model_path)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)
# summary(model,(3, 224, 224))

# ######################################################################################
# print("\n###########################################################################\n")

# import torch
# import torchvision
# from thop import profile
# from thop import clever_format

# model = torchvision.models.resnet18()
# # model = torch.jit.load(model_path)
# input = torch.randn(1, 3, 224, 224)
# macs, params = profile(model, inputs=(input, ))
# macs, params = clever_format([macs, params], "%.3f")

# print(macs)
# print(params)

# ######################################################################################
# print("\n###########################################################################\n")

# # 统计参数量
# import torch 
# from torchvision.models import resnet50
# import numpy as np

# Total_params = 0
# Trainable_params = 0
# NonTrainable_params = 0

# # model = resnet50()
# model = torch.jit.load(model_path)

# for name, parameters in model.named_parameters():
#     print(name, ':', np.prod(parameters.size()))

# for param in model.parameters():
#     mulValue = np.prod(param.size())  # 使用numpy prod接口计算参数数组所有元素之积
#     Total_params += mulValue  # 总参数量
#     if param.requires_grad:
#         Trainable_params += mulValue  # 可训练参数量
#     else:
#         NonTrainable_params += mulValue  # 非可训练参数量

# print(f'Total params: {Total_params / 1e6}M')
# print(f'Trainable params: {Trainable_params/ 1e6}M')
# print(f'Non-trainable params: {NonTrainable_params/ 1e6}M')

# # ######################################################################################
# # print("\n###########################################################################\n")

# # 统计参数量
# def get_parameter_number(model):
#     total_num = sum(p.numel() for p in model.parameters())
#     trainable_num = sum(p.numel() for p in model.parameters() if p.requires_grad)
#     return {'Total': total_num, 'Trainable': trainable_num}

# model = torch.jit.load(model_path)
# result = get_parameter_number(model)
# print(model.parameters())
# print(result['Total'],result['Trainable']) #打印参数量

# ######################################################################################
# print("\n###########################################################################\n")

# import torchvision.models as models
# import torch
# from ptflops import get_model_complexity_info

# with torch.cuda.device(0):
#     #net = models.densenet161()
#     net = torch.jit.load(model_path)
#     macs, params = get_model_complexity_info(net, (3, 224, 224), as_strings=True, 
#         print_per_layer_stat=True, verbose=True)
#     print('{:<30}  {:<8}'.format('Computational complexity: ', macs))
#     print('{:<30}  {:<8}'.format('Number of parameters: ', params))

# ######################################################################################
# print("\n###########################################################################\n")

# from torchvision.models import resnet18
# from nni.compression.pytorch.utils.counter import count_flops_params

# # model = resnet18()
# model = torch.jit.load(model_path)
# dummy_input = torch.randn(1, 3, 540, 960)
# flops, params, results = count_flops_params(model, dummy_input)

# ######################################################################################
# print("\n###########################################################################\n")

# from torchstat import stat
# from torchvision.models import resnet50

# # model = resnet50()
# model = torch.jit.load(model_path)
# model.eval()
# stat(model, (3, 540, 960))

# ######################################################################################
# print("\n###########################################################################\n")

# import torch
# import torchvision
# from pytorch_model_summary import summary

# # Model
# print('==> Building model..')
# # model = torchvision.models.alexnet(pretrained=False)
# model = torch.jit.load(model_path)

# dummy_input = torch.randn(1, 3, 540, 960)
# print(summary(model, dummy_input, show_input=False, show_hierarchical=False))

# pytorch_total_params = sum(p.numel() for p in model.parameters())
# trainable_pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

# print('Total - ', pytorch_total_params)
# print('Trainable - ', trainable_pytorch_total_params)
