
import os
import cv2
import time
from matplotlib.backend_bases import MouseEvent
import numpy as np

import onnx
import onnx_opcounter
import onnxruntime as ort
from onnx import helper, shape_inference
from onnx import AttributeProto, TensorProto, GraphProto
import onnx_tool

from tqdm import tqdm

def load_model(path):
    print("==> Load ONNX model '{}'".format(path))
    model = onnx.load(path)
    onnx.checker.check_model(model)

    # print("==> Print ONNX model '{}'".format(path))
    # print(model.graph.node)
    # print(model.graph.value_info)
    # print(model.graph.input)
    # print(model.graph.output)

    return model

def get_node(name, model):
    for i in range(len(model.graph.node)):
        if model.graph.node[i].name == name:
            node = model.graph.node[i]

    print(f"==> Get ONNX node '{name}'")
    print(node)

    return node

def del_node(name, model):
    graph = model.graph
    
    # demo for remove node with single input and output
    in_rename_map = {}
    
    for node_id, node in enumerate(graph.node):
        if node.name == name:
            in_name = node.input[0]
            out_name = node.output[0]
            in_rename_map = {out_name: in_name}
            del graph.node[node_id]
            break
    
    for node_id, node in enumerate(graph.node):
        for in_id, in_name in enumerate(node.input):
            if in_name in in_rename_map:
                node.input[in_id] = in_rename_map[in_name]

def infer(args):
    print("==> Inference ONNX model '{}'".format(args.path))
    session = ort.InferenceSession(args.path)
    # session = ort.InferenceSession(args.path, providers=['TensorrtExecutionProvider', 'CUDAExecutionProvider', 'CPUExecutionProvider'])
    input = np.random.randn(args.batch_size, args.channel, args.height, args.width).astype(np.float32)

    inputs = {session.get_inputs()[0].name: input}
    print(f"inputs: {inputs}")
    outputs = session.run(None, inputs)
    print("outputs: {}".format({session.get_outputs()[0].name: outputs}))

def make_pad():
    # 创建输入 (ValueInfoProto)
    x = helper.make_tensor_value_info('x', TensorProto.FLOAT, [3, 2])
    pads = helper.make_tensor_value_info('pads', TensorProto.FLOAT, [1, 4])
    value = helper.make_tensor_value_info('value', AttributeProto.FLOAT, [1])

    # 创建输出 (ValueInfoProto)
    y = helper.make_tensor_value_info('y', TensorProto.FLOAT, [3, 4])

    # 创建节点 (NodeProto) 
    node_def = helper.make_node(
        'Pad', # node name
        ['x', 'pads', 'value'], # inputs
        ['y'], # outputs
        mode='constant', # attributes
    )

    # 创建图 (GraphProto)
    graph_def = helper.make_graph(
        [node_def],
        'pad',
        [x, pads, value],
        [y],
    )

    # 创建模型 (ModelProto)
    model_def = helper.make_model(graph_def, producer_name='onnx-opt')
    print('The model is:\n{}'.format(model_def))
    onnx.checker.check_model(model_def)
    print('The model is checked!')

    # 导出模型
    onnx.save(model_def, "./pad.onnx")

def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description='PyTorch Classification Training')

    parser.add_argument('--path', default='./efformer.onnx', help='model path')
    parser.add_argument('--batch-size', default=1, type=int)
    parser.add_argument('--channel', default=3, type=int)
    parser.add_argument('--width', default=960, type=int)
    parser.add_argument('--height', default=540, type=int)

    args = parser.parse_args()

    return args

if __name__ == '__main__':
    args = parse_args()

    # # inference
    # infer(args)

    # load model
    model = load_model(args.path)

    # # eliminate softmax
    # node = get_node("Exp_620", model)
    # node = get_node("ReduceSum_621", model)
    # node = get_node("Div_622", model)
    # del_node("Exp_620", model)
    # del_node("ReduceSum_621", model)
    # del_node("Div_622", model)
    # onnx.save(model, args.path.replace(".onnx", "_cast.onnx"))

    # # make pad node
    # make_pad()

    # # onnx opcounter
    # print(onnx_opcounter.calculate_macs(model))
    # print(onnx_opcounter.calculate_params(model))

    # # profile MACs, memory, params
    # # # for dynamic input shape
    # # input = np.random.randn(args.batch_size, args.channel, args.height, args.width).astype(np.float32)
    # # inputs = {"input": input}
    # # onnx_tool.model_profile(args.path, inputs, None)
    # onnx_tool.model_profile(args.path, None, None) # pass file name
    # onnx_tool.model_profile(args.path, savenode='node_table.txt') # save profile table to txt file
    # onnx_tool.model_profile(args.path, savenode='node_table.csv') # save profile table to csv file
