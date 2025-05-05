import torch
import numpy as np
import matplotlib.pyplot as plt

data_path = "/Users/jorgebarahona/Downloads/datos02 (1).txt"
data = np.loadtxt(data_path, delimiter=',')  
X = data[:, 0:2]  
Y = data[:, -1]  
normalize = True 

if normalize:
    X = (X - np.mean(X, axis=0)) / np.std(X, axis=0)
    Y = (Y - np.mean(Y)) / np.std(Y)

X_tensor = torch.tensor(X, dtype=torch.float32)  
Y_tensor = torch.tensor(Y, dtype=torch.float32) 
weights = torch.randn(2, 1, requires_grad=True)  
bias = torch.randn(1, requires_grad=True)  

learning_rate = 0.01
num_epochs = 1550

losses = []

for epoch in range(num_epochs):
    predictions = X_tensor @ weights + bias  

    loss = torch.mean((predictions - Y_tensor) ** 2)
    losses.append(loss.item())  

    loss.backward()

    with torch.no_grad():
        weights -= learning_rate * weights.grad
        bias -= learning_rate * bias.grad

        weights.grad.zero_()
        bias.grad.zero_()


print(f"Trained weights: {weights.detach().numpy()}")
print(f"Trained bias: {bias.detach().numpy()}")

fitted_values = (X_tensor @ weights + bias).detach().numpy()

# Create meshgrid for the plane
x_min, x_max = X[:, 0].min(), X[:, 0].max()
y_min, y_max = X[:, 1].min(), X[:, 1].max()
x_mesh, y_mesh = np.meshgrid(np.linspace(x_min, x_max, 50), np.linspace(y_min, y_max, 50))

print(x_mesh)
# Predict values for the meshgrid
mesh_input = np.c_[x_mesh.ravel(), y_mesh.ravel()]
mesh_tensor = torch.tensor(mesh_input, dtype=torch.float32)
z_mesh = (mesh_tensor @ weights + bias).detach().numpy().reshape(x_mesh.shape)

fig = plt.figure(figsize=(12, 6))
ax = fig.add_subplot(121, projection='3d')

ax.scatter(X[:, 0], X[:, 1], Y, label="Observed Data", color="blue")
ax.plot_surface(x_mesh, y_mesh, z_mesh, color="red", alpha=0.5)
ax.set_xlabel("X1")
ax.set_ylabel("X2")
ax.set_zlabel("Y")
ax.set_title("3D Scatter with Fitted Plane")
ax.legend()

ax2 = fig.add_subplot(122)
ax2.plot(range(num_epochs), losses, label="Loss", color="green")
ax2.set_xlabel("Epoch")
ax2.set_ylabel("Loss")
ax2.set_title("Loss per Epoch - Min loss: {:.4f}".format(min(losses)))
ax2.legend()

plt.tight_layout()
plt.show()