
from email.policy import strict
import os
import cv2
import time
import argparse
import torch
import torchvision
import numpy as np

import onnx
import onnxruntime as ort

from tqdm import tqdm

def export(args):
    torch.set_grad_enabled(False)

    model = torchvision.models.__dict__[args.model]()
    checkpoint = torch.load(args.path, map_location=torch.device('cpu'))
    model.load_state_dict(checkpoint["model"])
    model.eval()

    device = 'cuda'
    output_onnx = args.path.replace(".pth", ".onnx")

    # ------------------------ export -----------------------------
    print("==> Exporting model to ONNX format at '{}'".format(output_onnx))
    input_names = ['input']
    output_names = ['output']

    input_tensor = torch.randn(args.batch_size, args.channel, args.height, args.width, device=device)

    torch.onnx.export(model.cuda(), input_tensor, output_onnx, export_params=True, verbose=False,
                      input_names=input_names, output_names=output_names, opset_version=10,
                      do_constant_folding=True,
                      dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}})

    # ------------------------ run -----------------------------
    print("==> Checking ONNX model '{}'".format(output_onnx))
    onnx_model = onnx.load(output_onnx)
    onnx.checker.check_model(onnx_model)

    print("==> Inference ONNX model '{}'".format(output_onnx))
    session = ort.InferenceSession(output_onnx, providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
    # x = np.random.randn(args.batch_size, args.channel, args.height, args.width).astype(np.float32)
    x = input_tensor.cpu().numpy().astype(np.float32)

    inputs = {session.get_inputs()[0].name: x}
    # print(f"inputs: {inputs}")
    outputs = session.run(None, inputs)
    # print("outputs: {}".format({session.get_outputs()[0].name: outputs}))

    # ------------------------ compare -----------------------------
    print("==> Compare ONNX and pytorch model '{}'".format(args.model))
    with torch.no_grad():
        torch_output = model(input_tensor)

    # compare ONNX Runtime and PyTorch results
    np.testing.assert_allclose(torch_output.cpu().numpy(), outputs[0], rtol=1e-03, atol=1e-05)
    print("Exported model has been tested with ONNXRuntime, and the result looks good!")

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='PyTorch Classification Training')

    parser.add_argument('--model', default='resnet18', help='model')
    parser.add_argument('--path', default='./resnet18.pth', help='model path')
    parser.add_argument('--batch-size', default=1, type=int)
    parser.add_argument('--channel', default=3, type=int)
    parser.add_argument('--width', default=84, type=int)
    parser.add_argument('--height', default=84, type=int)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()
    export(args)
