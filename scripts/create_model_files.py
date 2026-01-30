#!/usr/bin/env python3
"""
Script to create placeholder model files for testing.

Creates both ONNX and TorchScript versions of:
- LLM (Large Language Model)
- KWS (Keyword Spotting Model)
"""

import torch
import torch.nn as nn
import onnx
from onnx import helper, TensorProto
import numpy as np
from pathlib import Path


def create_llm_onnx(models_dir: Path):
    """Create a simple LLM model in ONNX format."""
    # Input
    input_tensor = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 128])
    # Output
    output_tensor = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 128])
    
    # Weights
    weight = helper.make_tensor(
        name='weight',
        data_type=TensorProto.FLOAT,
        dims=[128, 128],
        vals=np.random.randn(128, 128).astype(np.float32).flatten().tolist()
    )
    
    # Node
    node = helper.make_node(
        'MatMul',
        inputs=['input', 'weight'],
        outputs=['output']
    )
    
    # Graph
    graph = helper.make_graph(
        [node],
        'llm_model',
        [input_tensor],
        [output_tensor],
        [weight]
    )
    
    # Model
    model = helper.make_model(graph, producer_name='model-compilation')
    onnx.save(model, str(models_dir / "llm.onnx"))
    print(f"✓ Created {models_dir / 'llm.onnx'}")


def create_kws_onnx(models_dir: Path):
    """Create a simple KWS model in ONNX format."""
    # Input (audio features)
    input_tensor = helper.make_tensor_value_info('input', TensorProto.FLOAT, [1, 40, 32])
    # Output (keyword classes)
    output_tensor = helper.make_tensor_value_info('output', TensorProto.FLOAT, [1, 10])
    
    # Flatten node
    flatten_node = helper.make_node(
        'Flatten',
        inputs=['input'],
        outputs=['flattened'],
        axis=1
    )
    
    # Weights
    weight = helper.make_tensor(
        name='weight',
        data_type=TensorProto.FLOAT,
        dims=[1280, 10],
        vals=np.random.randn(1280, 10).astype(np.float32).flatten().tolist()
    )
    
    # MatMul node
    matmul_node = helper.make_node(
        'MatMul',
        inputs=['flattened', 'weight'],
        outputs=['output']
    )
    
    # Graph
    graph = helper.make_graph(
        [flatten_node, matmul_node],
        'kws_model',
        [input_tensor],
        [output_tensor],
        [weight]
    )
    
    # Model
    model = helper.make_model(graph, producer_name='model-compilation')
    onnx.save(model, str(models_dir / "kws.onnx"))
    print(f"✓ Created {models_dir / 'kws.onnx'}")


class SimpleLLM(nn.Module):
    """Simple LLM model for TorchScript."""
    
    def __init__(self):
        super(SimpleLLM, self).__init__()
        self.linear = nn.Linear(128, 128)
    
    def forward(self, x):
        return self.linear(x)


def create_llm_torchscript(models_dir: Path):
    """Create a simple LLM model in TorchScript format."""
    model = SimpleLLM()
    model.eval()
    example_input = torch.randn(1, 128)
    traced_model = torch.jit.trace(model, example_input)
    torch.jit.save(traced_model, str(models_dir / "llm.pt"))
    print(f"✓ Created {models_dir / 'llm.pt'}")


class SimpleKWS(nn.Module):
    """Simple KWS model for TorchScript."""
    
    def __init__(self):
        super(SimpleKWS, self).__init__()
        self.flatten = nn.Flatten(start_dim=1)
        self.linear = nn.Linear(40 * 32, 10)
    
    def forward(self, x):
        x = self.flatten(x)
        return self.linear(x)


def create_kws_torchscript(models_dir: Path):
    """Create a simple KWS model in TorchScript format."""
    model = SimpleKWS()
    model.eval()
    example_input = torch.randn(1, 40, 32)
    traced_model = torch.jit.trace(model, example_input)
    torch.jit.save(traced_model, str(models_dir / "kws.pt"))
    print(f"✓ Created {models_dir / 'kws.pt'}")


def main():
    """Main function to create all model files."""
    # Get project root (parent of scripts directory)
    project_root = Path(__file__).parent.parent
    models_dir = project_root / "data" / "models"
    
    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)
    
    print("Creating model files...")
    print(f"Target directory: {models_dir}")
    print()
    
    try:
        # Create ONNX models
        create_llm_onnx(models_dir)
        create_kws_onnx(models_dir)
        
        # Create TorchScript models
        create_llm_torchscript(models_dir)
        create_kws_torchscript(models_dir)
        
        print()
        print("✅ All model files created successfully!")
        print()
        print("Created files:")
        for model_file in sorted(models_dir.glob("*.onnx")) + sorted(models_dir.glob("*.pt")):
            size = model_file.stat().st_size
            print(f"  - {model_file.name} ({size:,} bytes)")
        
    except Exception as e:
        print(f"❌ Error creating models: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
