# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 14:37:50 2021

@author: HashiriNio
"""

from entity_get import EntityObtainer
from candidate_scoring import candi_scoring
import candidate_get
import sys

#input_question = '计算机网络是什么'#需要更改输入

entity_obtainer = EntityObtainer()
scorer = candi_scoring()

input_question = input('请输入问题:')
entities = entity_obtainer.mention_get(input_question)
print('得到的mention为:',entities)

candidates = []
for entity in entities:
    candidates += candidate_get.GetPaths(entity)
if candidates == []:
    sys.exit('没有符合的实体')
print('候选路径:',candidates)

#candidates = [('计算机网络', '模型'), ('计算机网络', '模型', '网络结构')]

the_path,the_score = scorer.scoring(input_question,candidates)
answer = candidate_get.get_answer(the_path)
if the_score > 0.45:
    print('查询路径:',the_path)
    print('答案:',answer,'\n得分:',str(the_score))
else:
    print('没有合适的答案')

    