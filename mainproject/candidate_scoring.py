# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 14:40:24 2021

@author: HashiriNio
"""

import numpy as np
#import pandas as pd
#import pickle
from keras_bert import Tokenizer, get_custom_objects
import codecs as cs
from keras.models import load_model
from candidate_get import bridge


class candi_scoring():
    def __init__(self):
        self.max_seq_len = 20
        #加载bert字典
        dict_path = r'D:\final_design\Final_one\bert\vocab.txt'
        token_dict = {}
        with cs.open(dict_path, 'r', 'utf8') as reader:
            for line in reader:
                token = line.strip()
                token_dict[token] = len(token_dict)
        self.tokenizer = Tokenizer(token_dict)
        #加载评分模型
        self.model = load_model(r'D:\final_design\Final_one\data\model\model_match_general5_1.h5',custom_objects=get_custom_objects())
        print('loaded')
    
    def get_tokens(self, seq1, seq2):
        #seq1为str，seq2为list
        X1_1, X1_2, X2_1, X2_2 = [] ,[],[],[]
        x1_1, x1_2 = self.tokenizer.encode(first = seq1, max_len = self.max_seq_len)
        for i in range(len(seq2)):
            #x1_1,x1_2 = self.tokenizer.encode(first = seq1[i],max_len = self.max_seq_len)
            x2_1, x2_2 = self.tokenizer.encode(first = seq2[i], max_len = self.max_seq_len)
            X1_1.append(x1_1)
            X1_2.append(x1_2)
            X2_1.append(x2_1)
            X2_2.append(x2_2)
        
        return np.array(X1_1), np.array(X1_2), np.array(X2_1), np.array(X2_2)
    
    def get_ques(self, candidates):
        #candidates = [(,),(,)]
        candidate_paths = []
        for candidate in candidates:
            if len(candidate) == 2:
                candidate_paths.append(candidate[0]+'的'+candidate[1]+'是？')
            else:
                candidate_paths.append(candidate[0]+'的'+candidate[1]+'的'+candidate[2]+'是？')
        return candidate_paths
    
    def get_bridged_ques(self,paths):
        # paths = [(x1,r1,r2,x2),()]
        bridged_q = []
        for path in paths:
            bridged_q.append(path[0] + '和' + path[3] + '的相同点是？')
            bridged_q.append(path[0] + '和' + path[3] + '的区别是？')
        return bridged_q

    def scoring(self, question, candidates):
        topk = 5
        candidate_ques = self.get_ques(candidates)
        in1_1, in1_2, in2_1, in2_2 = self.get_tokens(question, candidate_ques)
        score = self.model.predict([in1_1, in1_2, in2_1, in2_2])
        score1 = []
        for i in score:
            score1.append(i[0])
        temp = sorted(score1, reverse=1)
        Index = []
        for i in range(min(topk, len(temp))):
            Index.append(score1.index(temp[i]))
        # 桥接打分
        bridged_paths = bridge(Index, candidates)
        # print('bridged_paths',bridged_paths)
        if bridged_paths == []:
            b_one = 0
        else:
            bridged_ques = self.get_bridged_ques(bridged_paths)  # 问题数目是路径的两倍
            # print('bridged_ques',bridged_ques)
            in1_1, in1_2, in2_1, in2_2 = self.get_tokens(question, bridged_ques)
            scoreb = self.model.predict([in1_1, in1_2, in2_1, in2_2])
            print('桥接得分',scoreb)
            score2 = []
            for i in scoreb:
                score2.append(i[0])
            tempb = sorted(score2, reverse=1)
            bindex = score2.index(tempb[0])
            b_one = tempb[0]
        # 选择得分最高的路径
        mark = 0
        if b_one > score1[Index[0]]:
            print(bindex / 2)
            the_path = bridged_paths[int(bindex / 2)]
            if bindex % 2 == 1:
                mark = 1
            the_score = b_one
            print(question, bridged_ques[bindex])
        else:
            the_path = candidates[Index[0]]
            the_score = score1[Index[0]]
        return the_path, the_score, mark