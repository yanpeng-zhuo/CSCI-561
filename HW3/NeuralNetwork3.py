'''
Author: Yanpeng Zhuo
Github: https://github.com/zhuoyanpeng
Date: 2021-11-02 17:34:15
LastEditors: Yanpeng Zhuo
Description: file content
'''
import time
import math
import numpy as np
import sys


class Learner():
    ## 100 0.02 highest 97.86%
    def __init__(self, batch_size=100, learning_rate=0.02, epoch=60):
        self.output = 'test_predictions.csv'
        self.X_train = []
        self.X_test = []
        self.Y_train = []
        self.Y_test = []
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epoch = epoch
        self.activation = []
        self.layer = []
        ## Xavier Weight
        ## range of weight and bias: -(1.0 / sqrt(n)), (1.0 / sqrt(n))
        coefficient = 1.0/math.sqrt(784)
        self.weight = [
            (np.random.random((512,784))*2-1) * coefficient,
            (np.random.random((256,512))*2-1) * coefficient,
            (np.random.random((10,256))*2-1) * coefficient
        ]
        self.bias = [
            (np.random.random((512,1))*2-1) * coefficient,
            (np.random.random((256,1))*2-1) * coefficient,
            (np.random.random((10,1))*2-1) * coefficient
        ]
        
    def read_file(self, input1, input2, input3):
        with open(input1, 'r') as f:
            images = f.readlines()
            for image in images:
                self.X_train.append(np.array(image.strip().split(',')).astype(int))
            self.X_train = np.transpose(self.X_train)

        with open(input2, 'r') as f:
            tests = f.readlines()
            trains = []
            for test in tests:
                trains.append(int(test.strip()))
            trains = np.array(trains)

            self.X_test = np.zeros((10, trains.size))
            for index in range(len(trains)):
                self.X_test[trains[index]][index] = 1

        with open(input3, 'r') as f:
            images = f.readlines()
            for image in images:
                self.Y_train.append(np.array(image.strip().split(',')).astype(int))
            self.Y_train = np.transpose(self.Y_train)

        with open("test_label.csv", 'r') as f:
            tests = f.readlines()
            trains = []
            for test in tests:
                trains.append(int(test.strip()))
            self.Y_test = np.array(trains)

    def write(self):
        self.forward(self.Y_train)
        pred = np.argmax(self.layer[2], axis=0)
        with open("test_predictions.csv", 'w') as f:
            for i in range(len(pred)):
                f.write(str(pred[i]) + '\n')

    def get_batches(self):
        batches = []
        ## if batch_size is 100, size is 60000, we have 600 sets of data
        for i in range(math.floor(len(self.X_train[0])/self.batch_size)):
            batches.append((self.X_train[:,i*self.batch_size:(i+1)*self.batch_size], self.X_test[:,i*self.batch_size:(i+1)*self.batch_size]))
        return batches

    def sigmoid(self, activation):
        ## float 64 can only handle exp number in range(-exp(709.78), exp(709.78))
        ## we need to use np.clip to rerange it
        activation = np.clip(activation, -709.78, 709.78)
        return 1.0/(1.0 + np.exp(-activation))

    def softmax(self, activation):
        e = np.exp(activation)
        return e / np.sum(e, axis=0)

    def forward(self, train):
        self.activation = []
        self.layer = []
        for i in range(3):
            if i-1<0:
                self.activation.append(np.dot(self.weight[i], train) + self.bias[i])
            else:
                self.activation.append(np.dot(self.weight[i], self.layer[i-1]) + self.bias[i])
            if i==2:
                self.layer.append(self.softmax(self.activation[i]))
            else:
                self.layer.append(self.sigmoid(self.activation[i]))

    def undo_sigmoid(self, backward_activation, activation):
        # x = ln(y/(1-y))
        sigmoid = self.sigmoid(activation)
        return (sigmoid - sigmoid*sigmoid) * backward_activation

    def backward(self, train, test):
        newWeight = []
        newBias = []
        backward_activation = []
        backward_layer = []

        backward_layer.append(self.layer[2] - test)
        
        backward_activation.append(np.dot(self.weight[2].T, backward_layer[0]))
        backward_layer.append(self.undo_sigmoid(backward_activation[0], self.activation[1]))
        
        backward_activation.append(np.dot(self.weight[1].T, backward_layer[1]))
        backward_layer.append(self.undo_sigmoid(backward_activation[1], self.activation[0]))

        for i in range(3):
            if 1-i<0:
                newWeight.insert(0, np.dot(backward_layer[i], train.T) / self.batch_size)
            else:
                newWeight.insert(0, np.dot(backward_layer[i], self.layer[1-i].T) / self.batch_size)
            newBias.insert(0, np.sum(backward_layer[i]) / self.batch_size)

        # Update the weights and bias for next batch
        for i in range(3):
            self.weight[i] = self.weight[i] - (self.learning_rate * newWeight[i])
            self.bias[i] = self.bias[i] - (self.learning_rate * newBias[i])
        
    def training(self):
        for i in range(self.epoch):
            batches = self.get_batches()
            ## train the portion one by one
            for batche in batches:
                train, test = batche
                self.forward(train)
                self.backward(train, test)

            self.prediction_test()

    def prediction_test(self):
        self.forward(self.Y_train)
        pred = np.argmax(self.layer[2], axis=0)
        print(np.sum(pred == self.Y_test) / len(pred) * 100, '%')

if __name__ == "__main__":
    start = time.time()
    learner = Learner()
    learner.read_file(sys.argv[1], sys.argv[2], sys.argv[3])
    learner.training()
    learner.write()
    print(time.time() - start)
