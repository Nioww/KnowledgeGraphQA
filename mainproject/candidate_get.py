# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 14:38:23 2021

@author: HashiriNio
"""

from neo4j import GraphDatabase
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "123456"))
session = driver.session()


def GetPaths(entity):
    #entity='物理层'
    #一跳路径
    query_1 = "match (a:Entity)-[r1:hasPart]->() where a.name=$name return DISTINCT r1.name"
    result = session.run(query_1, name=entity)
    path_one = []
    for i in result:
        path_one.append((entity, i['r1.name']))
    #两跳路径
    path_two = []
    query_2 = "match (a:Entity)-[r1:hasPart]-()-[r2:hasPart]->() where a.name=$name return DISTINCT r1.name,r2.name"
    result = session.run(query_2, name=entity)
    for i in result:
        path_two.append((entity, i['r1.name'], i['r2.name']))
    #print(path_one,'\n',path_two)
    return path_one+path_two


def bridge(index, candidates):
    #得到所有需要桥接的实体
    entities = []
    for i in range(len(index)):
        if candidates[index[i]][0] not in entities:
            entities.append(candidates[index[i]][0])
    #得到桥接后的路径
    paths = []
    if len(entities) < 2:
        return []
    else:
        query = "match (a:Entity)-[r1:hasPart]->()<-[r2:hasPart]-(b:Entity) where a.name=$name AND b.name=$name2 return DISTINCT r1.name,r2.name"
        query2 = "match (a:Entity)<-[r1:hasPart]-()-[r2:hasPart]->(b:Entity) where a.name=$name AND b.name=$name2 return DISTINCT r1.name,r2.name"
        end = len(entities)
        for i in range(end - 1):
            for l in range(i + 1, end):
                result = session.run(query, name=entities[i], name2=entities[l])
                result2 = session.run(query2, name=entities[i], name2=entities[l])
                for k in result:
                    if (entities[i], 1, 1, entities[l]) not in paths:
                        paths.append((entities[i], 1, 1, entities[l]))
                for k in result2:
                    if (entities[i], 1, 1, entities[l]) not in paths:
                        paths.append((entities[i], 1, 1, entities[l]))
        return paths


def get_answer(path, mark):
    if mark == 1:  # 相异问题
        query = "match (a:Entity)-[r1:hasPart]->(b:Entity) where a.name=$name return DISTINCT r1.name,b.name"
        resulta = session.run(query, name=path[0])
        resultb = session.run(query, name=path[3])
        ra = {}
        for i in resulta:
            ra[i['r1.name']] = [i['b.name'], 0]
        for i in resultb:
            if i['r1.name'] in ra.keys():
                ra[i['r1.name']][1] = i['b.name']
        answer = ''
        for i in ra.keys():
            if ra[i][1] == 0:
                continue
            if ra[i][0] == ra[i][1]:
                continue
            answer += path[0] + '的' + i + '是' + ra[i][0] + ',' + path[3] + '的' + i + '是' + ra[i][1] + '。'
        return answer

    if len(path) == 2:
        query = "match (a:Entity)-[r1:hasPart]->(b:Entity) where a.name=$name AND r1.name=$name2 return DISTINCT b.name"
        result = session.run(query, name=path[0], name2=path[1])
    elif len(path) == 3:  # 两条
        query = "match (a:Entity)-[r1:hasPart]-()-[r2:hasPart]->(b:Entity) where a.name=$name AND r1.name=$name2 AND r2.name=$name3 return DISTINCT b.name"
        result = session.run(query, name=path[0], name2=path[1], name3=path[2])
    else:  # 桥接的路径解决相同点问题
        query = "match (a:Entity)-[r1:hasPart]->(b:Entity)<-[r2:hasPart]-(c:Entity) where a.name=$name AND c.name=$name2 return DISTINCT r1.name,b.name"
        result = session.run(query, name=path[0], name2=path[3])
        query2 = "match (a:Entity)<-[r1:hasPart]-(b:Entity)-[r2:hasPart]->(c:Entity) where a.name=$name AND c.name=$name2 return DISTINCT r1.name,b.name"
        result2 = session.run(query2, name=path[0], name2=path[3])
        final_answer = ''
        k = ''
        for l in result2:
            k = '它们都是' + l['b.name'] + '的' + l['r1.name']
        if k != '':
            k += '。'
            final_answer += k
        count = 0
        answer = '它们的'
        for i in result:
            if count == 0:
                answer += i['r1.name'] + '都有' + i['b.name']
                count += 1
            else:
                answer += ';' + i['r1.name'] + '都有' + i['b.name']  # 如果有多个答案
        if answer != '它们的':
            answer += '。'
            final_answer += answer
        return final_answer
    count = 0
    for i in result:
        if count == 0:
            answer = i['b.name']
            count += 1
        else:
            answer += (';' + i['b.name'])  # 如果有多个答案
    return answer
