import torch
import torch.nn as nn


class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(32, 20)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(20, 12)
        self.sigmoid = nn.Sigmoid()
        self.fc3 = nn.Linear(12,4)
        self.softmax = nn.Softmax(dim=1)
    

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.sigmoid(x)
        x = self.fc3(x)
        x = self.softmax(x)
        return x