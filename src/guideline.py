from typing import List
import json
from utils import *



def main_sequence_gen(main_points: any):
    # 生成学习计划
    result = []
    content = json.dumps(main_points, indent=4)
    res = "No brackets found or incomplete pair"

    while res == "No brackets found or incomplete pair":
        try:
            question = "The content above gives you some knowledge points. Please based on the dependence of the knowledge points, generate a learning plan. If a knowledge point needs some prerequisites, please put those prerequired knowledge points in front."
            appendix = "Your answer must be in the form of a list of strings. Do not include annotation or anything else! Here is the example: [xx, xx, xx] where each string is the name of a knowledge point."
            prompt = content + question + appendix
            res = query_gpt4(prompt)  
            res = extract_including_brackets(res) 

            data_list = ast.literal_eval(res)
            if not isinstance(data_list, list):
                raise ValueError("Result is not a list")

            print("Main study plan successfully generated.")
            result = data_list
            return result

        except (SyntaxError, ValueError) as e:
            print(f"Error occurred: {e}. Retrying...")
            res = "No brackets found or incomplete pair"
    '''
    返回类型：
    [ # 知识图谱，由于 PPT 的线性性，可以直接用列表，用于前端计划展示
            {
                sequence: number, # 学习序列的顺序
                points: [
                    str,
                    str,
                    ...
                ] # 在这个学习序列上可以学习的子知识点
            },
            ...
        ]
    '''
    
def sub_sequence_gen(child: any, index: int):
    # 生成学习计划
    result = {}
    result["sequence"] = index + 1
    content = []
    for i in child :
        temp = {"name":i["name"],"definition":i["definition"],"information":i["information"],"usage":i["usage"]}
        content.append(temp)
    content = json.dumps(content, indent=4)
    res = "No brackets found or incomplete pair"
    while res == "No brackets found or incomplete pair":
        try:
            question = "The content above give you some knowledge points. Please based on the dependence of the knowledge points, generate a learning plan. If a knowledge point needs some prerequisites, please put those prerequired knowledge points in front."
            appendix = "Your answer must be in the form of a list of string. Do not include annotation or anything else! Here is the example: ['xx', 'xx', 'xx'] each string is the name of a knowledge point."
            prompt = content + question + appendix
            res = query_gpt4(prompt) 
            res = extract_including_brackets(res)  

            # 确保结果是有效的列表
            data_list = ast.literal_eval(res)
            if not isinstance(data_list, list):
                raise ValueError("Result is not a list")
            
            print("Sub study plan successfully generated.")
            return data_list

        except (SyntaxError, ValueError) as e:
            print(f"Error occurred: {e}. Retrying...")
            res = "No brackets found or incomplete pair"
    '''
    返回类型：
    [ # 知识图谱，由于 PPT 的线性性，可以直接用列表，用于前端计划展示
            {
                sequence: number, # 学习序列的顺序
                points: [
                    str,
                    str,
                    ...
                ] # 在这个学习序列上可以学习的子知识点
            },
            ...
        ]
    '''
