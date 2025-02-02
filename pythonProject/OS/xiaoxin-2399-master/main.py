import torch
import torch.nn as nn
import torch.functional as F 
from tqdm import tqdm
from model.mscred import MSCRED
from utils.data import load_data
import matplotlib.pyplot as plt
import numpy as np
import os

def train(dataLoader, model, optimizer, epochs, device):
    model = model.to(device)
    print("------training on {}-------".format(device))
    epochs = 1  # 简化训练时间，实际使用中去掉
    for epoch in range(epochs):
        train_l_sum,n = 0.0, 0
        for x in tqdm(dataLoader):  # 一个数据; [1, 5, 3, 30, 30]
            x = x.to(device)
            x = x.squeeze()  # [5, 3, 30, 30]: 5个时间步, 3个窗口, 30*30的相似矩阵
            # x[-1]:最后一个时间步
            l = torch.mean((model(x)-x[-1].unsqueeze(0))**2)  # 均方误差
            train_l_sum += l
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
            n += 1
            #print("[Epoch %d/%d][Batch %d/%d] [loss: %f]" % (epoch+1, epochs, n, len(dataLoader), l.item()))
            
        print("[Epoch %d/%d] [loss: %f]" % (epoch+1, epochs, train_l_sum/n))

def test(dataLoader, model):
    print("------Testing-------")
    index = 800
    loss_list = []
    reconstructed_data_path = "./data/matrix_data/reconstructed_data/"
    os.makedirs(reconstructed_data_path, exist_ok=True)
    
    with torch.no_grad():
        for x in dataLoader:
            x = x.to(device)
            x = x.squeeze()
            reconstructed_matrix = model(x)  # 计算每个测试集
            path_temp = os.path.join(reconstructed_data_path, 'reconstructed_data_' + str(index) + ".npy")
            np.save(path_temp, reconstructed_matrix.cpu().detach().numpy())
            # l = criterion(reconstructed_matrix, x[-1].unsqueeze(0)).mean()
            # loss_list.append(l)
            # print("[test_index %d] [loss: %f]" % (index, l.item()))
            index += 1


if __name__ == '__main__':
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("device is", device)
    dataLoader = load_data()

    mscred = MSCRED(3, 256)  # 定义模型

    # 训练阶段
    # mscred.load_state_dict(torch.load("./checkpoints/model1.pth"))
    optimizer = torch.optim.Adam(mscred.parameters(), lr = 0.0002)
    train(dataLoader["train"], mscred, optimizer, 10, device)
    print("保存模型中....")
    torch.save(mscred.state_dict(), "./checkpoints/model2.pth")

    # # 测试阶段
    mscred.load_state_dict(torch.load("./checkpoints/model2.pth"))
    mscred.to(device)
    test(dataLoader["test"], mscred)