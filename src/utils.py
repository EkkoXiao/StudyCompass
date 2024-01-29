from langchain.document_loaders import UnstructuredPowerPointLoader, PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.document_loaders import TextLoader
import tempfile
from pptx import Presentation  
from pptx.enum.shapes import MSO_SHAPE_TYPE  
from PIL import Image  
import os
from typing import Tuple
import json
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import ast
from openai import OpenAI
import requests
import re



def query_gpt4(prompt):
    client = OpenAI()

    completion = client.chat.completions.create(
    model="gpt-4-1106-preview",
    messages=[
        {"role": "system", "content": "You are a teacher that is good at summarize key points for students"},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7
    )

    return completion.choices[0].message.content

def extract_including_brackets(res):
    start = res.find('[')
    end = res.rfind(']')
    if start != -1 and end != -1:
        return res[start:end+1]
    else:
        return "No brackets found or incomplete pair"

def ppt_knowledge_points_gen(metadata: any):
    # 根据获取的文字元信息提取主知识点
    titles = [item for item in metadata if item["type"] == "Title"]
    content = json.dumps(titles, indent=4)
    res = "No brackets found or incomplete pair"
    while( res == "No brackets found or incomplete pair"):
    
        question  ="Please seperate the following pages into no more than 10 continous parts based on the relevance of thier contents.Your answer must be in the form of a list of json.Here is the example:  [{id: xx,name : xx,pages : (xx, xx) },...]\
            'id' is the index of each category, in the order of 0、1、2. 'name' is the general description of the category,and should be a summary of all the pages included.'pages' is  a tuple that contains the \
                begin number and end number of the pages that belongs to the category.Remember that all the pages must be included,which means if we connect all the 'page' tuples end-to-end, it should cover all pages.The answer must be in Chinese."
        # res = chain.run(question)
        prompt = content + question
        res = query_gpt4(prompt)
        res = extract_including_brackets(res)
        # print(res)
        print("Main knowledge points successfully generated.")
    data_list = ast.literal_eval(res)
    return data_list
    '''
    返回值类型：
    [
        {
            id: number,
            name : str, # 知识点名
            pages : (number, number)  # 页数
        },
        ...
    ]
    '''

def knowledge_points_gen(metadata: any):
    # 根据获取的文字元信息提取主知识点
    content = json.dumps(metadata, indent=4)
    res = "No brackets found or incomplete pair"
    while True:
        try:
            question  ="Please seperate the given pages into no more than 10 continous parts based on the relevance of thier contents.Your answer must be in the form of a list of json.Here is the example:  [{id: xx,name : xx,pages : (xx, xx) },...]\
                'id' is the index of each category, in the order of 0、1、2. 'name' is the general description of the category,and should be a summary of all the pages included and each one must be unique,and it should not include symol '/' . 'pages' is  a tuple that contains the \
                    begin number and end number of the pages that belongs to the category.Remember that all the pages must be included,which means if we connect all the 'page' tuples end-to-end, it should cover all pages.The answer must be in Chinese."
            # res = chain.run(question)
            prompt = content + question
            res = query_gpt4(prompt)
            res = extract_including_brackets(res)
            
            data_list = ast.literal_eval(res)
            print("Main knowledge points successfully generated.")
            break
        except (SyntaxError, ValueError):
            # 如果解析失败，打印错误信息并继续循环
            print("Error in parsing the response. Trying again...")
    return data_list
    '''
    返回值类型：
    [
        {
            id: number,
            name : str, # 知识点名
            pages : (number, number)  # 页数
        },
        ...
    ]
    '''
    
def subpoints_gen(father:any,metadata:any):
    # 在指定页数范围之内生成子知识点信息
    father_point = father["name"]
    pages = father["pages"]
    begin = pages[0]
    end = pages[1]
    sub_mes = [item for item in metadata if item['page'] >= begin and item['page'] <= end]
    content = json.dumps(sub_mes, indent=4)
    res = "No brackets found or incomplete pair"
    while True:
        try:
            question  =f"The content above mainly talks about {father_point},Please seperate the given pages into no more than 5 continous parts based on the relevance of the pages.Pay attention that the begin page is {begin} and the end page is {end}."
            appendix = "If you can only seperate the content to less than 5 parts.It is totally OK.  \
            Your answer must be in the form of a list of json.. Do not include annotation or anything else! Here is the example:[{id: xx,pages:(xx,xx), name : xx,definition: xx,information:xx,usage:xx },...] 'id' is the index of each subpoints, in the order of 0、1、2. 'pages' is  a tuple that contains the begin number and end number of the pages that belongs to the subpoints.'name' is the general description of the subpoints and each one must be unique,and it should not include symol '/'.'definition' is the definition of the subpoints. 'information' is some descriptive information of the subpoints and it should be as specific and detailed as possible. 'usage' is the usage of the subpoints.Your answer must be in Chinese."
            prompt = content + question + appendix
            res = query_gpt4(prompt)
            res = extract_including_brackets(res)
            # print(res)
            data_list = ast.literal_eval(res)
            print("Sub knowledge points successfully generated.")
            break
        except (SyntaxError, ValueError):
            # 如果解析失败，打印错误信息并继续循环
            print("Error in parsing the response. Trying again...")
    return data_list
    '''
    返回值类型：
    [
        {
            id: number,
            pages : (from, to),
            name: str, # 子知识点名
            definition: str,
            information: str, # 子知识点的信息内容，可以根据 prompt 指定生成
            usage: str
        },
        ...
    ]
    '''

def add_image(child,db,id):
    for i in child :
        i["images"]= []
        begin = i['pages'][0]
        end = i['pages'][1]
        for root, dirs, files in os.walk(f"./data/workspace/{db}/{str(id)}/images"):
            for name in files:
                # 使用正则表达式来匹配并提取数字
                match = re.match(r'(\d+)-\d+\.\w+', name)

                # 检查是否有匹配
                if match:
                    # 提取第一个数字（a）
                    a = int(match.group(1))
                else:
                    print("文件名格式不符合预期")
                if a >= begin and a <= end:
                    image_path = f"./data/workspace/{db}/{str(id)}/images/{name}"
                    i["images"].append({"image":image_path})
    print("Images successfully added.")
    return child
   
                    
def save_mainpoints_to_file_as_json(mainpoints, file_path):

    # Write the metadata to the file as JSON
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(mainpoints, file, ensure_ascii=False, indent=4)             
   
    
def information_extension(child:any , father:any):
    # 根据上述生成信息进行联网拓展，暂时搁置
    # 设置 API 的 URL
    url = "http://127.0.0.1:7000/google/search"
    for i in child:
        if "searchresults" in i:
            continue 
        text = father["name"] + " " + i["name"]
        # text = "MiniDecaf项目实践"
        # 设置请求的参数
        params = {
            'lang': 'EN',
            'limit': 100,
            'text': text
        }

        # 发送 GET 请求
        response = requests.get(url, params=params)
        if(response.status_code == 503):
            i["searchresults"] = []
            print(response)
            print("No results are found.")
            continue
        # 检查请求是否成功
        while response.status_code != 200:
            response = requests.get(url, params=params)
            # print(response)
        
        wholetext = response.json()
        wholetext = json.dumps(wholetext, indent=4)
        # print(wholetext)
        topic = i["name"]
        res = "No brackets found or incomplete pair"
        while True:
            try:
                wholetext = "Here is some web pages and descriptions" + wholetext + "\n"
                content  =f"The target topic is : {topic},you need to select no more than 5 most related web pages from the text above.If some web page's description seems like advertisement or is totally unrelated to the target topic,you can delete it."
                question = "Your answer must be in the form of a list of json.Here is the example:  [{rank: xx,url : xx,description : xx },...],rank must be in the order 0、1、2.....,you can set a new rank for each search result.you do not need to include titles."
                # res = chain.run(question)
                prompt = wholetext + content + question
                res = query_gpt4(prompt)
                res = extract_including_brackets(res)
                # print(res)
                print("information_extension SUCCESSFUL.")
                data_list = ast.literal_eval(res)
                i["searchresults"] = data_list
                break
            except (SyntaxError, ValueError):
                print("Error in parsing the response. Trying again...")
    return child



def key_word_gen(metadata: any,file_path):
    content = json.dumps(metadata, indent=4)
    while True:
        try:
            question  ="Please based on the given content,give one key word to summarize it.The answer must be in Chinese and should be no more than 10 characters.Your answer should only include the key word and nothing else."
            # res = chain.run(question)
            prompt = content + question
            res = query_gpt4(prompt)
            print("Key words successfully generated.")
            with open(file_path, 'r', encoding='utf-8') as file:
                mainpoints = json.load(file)
                mainpoints["keyword"] = res
            save_mainpoints_to_file_as_json(mainpoints,file_path)
            break
        except (SyntaxError, ValueError):
            # 如果解析失败，打印错误信息并继续循环
            print("Error in parsing the response. Trying again...")


