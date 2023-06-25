# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 14:06:00 2021

@author: HashiriNio
"""

import jieba
import codecs as cs
#import pickle
#import time
import numpy as np
from keras_bert import Tokenizer,get_custom_objects
from keras.models import load_model
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"

#需要自备实体词典

class EntityObtainer():
    def __init__(self):
        self.seq_max_len = 20
        #加载bert字典
        dict_path = r'D:\final_design\Final_one\bert\vocab.txt'
        token_dict = {}
        with cs.open(dict_path, 'r', 'utf8') as reader:
            for line in reader:
                token = line.strip()
                token_dict[token] = len(token_dict)
        self.tokenizer = Tokenizer(token_dict)
        
        #加载NER模型
        model_path = r'D:\final_design\Final_one\data\model\model_ner_general.h5'
        custom_objects = get_custom_objects()
        self.ner_model = load_model(model_path,custom_objects =custom_objects)
        
        #加载实体词典
        mention_dic_path = r'D:\final_design\Final_one\data\mention_dict.txt'#需要替换
        mention_dict = {}
        with open(mention_dic_path,'r',encoding = 'utf-8') as f:
            for i in f:
                if i.strip():
                    mention_dict[i.strip()] = 1
        self.mention_dict = mention_dict
        #jieba.load_userdict('mention_dic_path')
        print('loaded')
    
    def restore_entity_from_corpus(self,predicty,question):
        def restore_entity_from_labels(labels,question):
            entitys = []
            str = ''
            labels = labels[1:-1]
            #print(labels,question)
            for i in range(min(len(labels),len(question))):
                if labels[i]==1:
                    str += question[i]
                else:
                    if len(str):
                        entitys.append(str)
                        str = ''
            if len(str):
                entitys.append(str) 
            return entitys
        all_entitys = []
        for i in range(len(predicty)):
            all_entitys.append(restore_entity_from_labels(predicty[i],question[i]))
            #print(predicty[i])
        return all_entitys
    
    def mention_get(self,question):
        #ner
        q = question#单问题输入
        mention_ner = []
        i1,i2 = self.tokenizer.encode(first = q,max_len = self.seq_max_len)
        i1 = np.array(i1)
        i2 = np.array(i2)        
        pre = self.ner_model.predict([np.array([i1,i2]),np.array([i2,i2])])
        pre = [1 if i >0.5 else 0 for i in pre[0]]
        #print(pre)
        predicty = self.restore_entity_from_corpus([pre],[q])
        #print(predicty)
        mention_ner = predicty[0]
        #for i in self.mention_dict.keys():
        #    for j in predicty[0]:
        #       if j in i:
        #            mention_ner.append(i)
        
        #分词
        mentions = []
        tokens = jieba.lcut(question)
        for t in tokens:
            if t in self.mention_dict.keys():
                mentions.append(t)
        
        for i in mention_ner:
            if i not in mentions:
                mentions.append(i)
        return mentions


