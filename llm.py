import torch

# Create two random tensors
x = torch.rand(3, 3)
y = torch.rand(3, 3)

# Add them
z = x + y

print("x:\n", x)
print("y:\n", y)
print("z = x + y:\n", z)

# Check if CUDA works
if torch.cuda.is_available():
    print("Running on GPU 🚀")
else:
    print("Running on CPU 🧠")
