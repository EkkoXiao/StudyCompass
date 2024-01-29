ONLY_FRONTEND = True

if ONLY_FRONTEND:
    WORKDIR = './test/'
else:
    WORKDIR = './data/'

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from pytkfaicons.fonts import get_font_icon
import fitz
from PIL import Image, ImageTk
import os
from tkhtmlview import HTMLLabel
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import tkinter.font as tkFont
# from database import bCreateDatabase, bAddFiles, bConversation

from hci_pipeline import *
import threading
import shutil
from any2pdf import *
 
app = None
def fFlush() :
    if app is not None:
        app.flush()

def bCreateDatabase(db: str) :
    base_dir = WORKDIR
    workspace_dir = "./workspace"
    db_work_dir = os.path.join(workspace_dir,db)
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    db_dir = os.path.join(base_dir, db)
    os.makedirs(db_dir, exist_ok=True)
    os.makedirs(db_work_dir, exist_ok=True)
    print(f"Created database directory '{db_dir}' and ensured workspace directory '{workspace_dir}' exists.")
    fFlush()

def curtail(names):
    number = len(names)
    content = ','.join(names) 
    res = "No brackets found or incomplete pair"
    while True:
        try:
            question  =f"I give you {number} phases separated by comma."
            question += "Please shorten each phase to make sure each one is shorter than 10 Chinese characters.But different points can not be exactly the same after shortening.\
                        If the phase is already less than 10 characters.\
                        You do not need to change it.Your answer must be in Chinese."
            question +=  f"And must in the form of a list of the same length:{number}.Here is an example:['xx','xx'].Do not add any explanation or comments.Just give me the answer."
            prompt = content + question
            res = query_gpt4(prompt)
            res = extract_including_brackets(res)           
            data_list = ast.literal_eval(res)
            if len(data_list) != number :
                print("Error!Restart")
                continue
            
            print("Main knowledge points successfully generated.")
            break
        except (SyntaxError, ValueError):
            # 如果解析失败，打印错误信息并继续循环
            print("Error in parsing the response. Trying again...")
    return data_list
# Example usage of the function
def bAddFiles(db: str, paths: [str]) :
    base_dir = f"./workspace/{db}"
    show_dir = f"{WORKDIR}/{db}"
    id = 0
    existing_ids = set()
    if os.path.exists(base_dir):
        for sub_dir in os.listdir(base_dir):
            if sub_dir.isdigit() and os.path.isdir(os.path.join(base_dir, sub_dir)):
                existing_ids.add(int(sub_dir))
    while id in existing_ids:
        id += 1  
    for path in paths:
        file_name = os.path.basename(path)
        file_dir = os.path.join(show_dir,str(id))
        os.makedirs(file_dir, exist_ok=True)
        file_dir = os.path.join(base_dir,str(id))
        os.makedirs(file_dir, exist_ok=True)
        dest_path = os.path.join(file_dir, file_name)
        shutil.copy2(path, dest_path)
        metadata = {"id":id}
        save_mainpoints_to_file_as_json(metadata,f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json")
        print(f"Copied '{path}' to '{dest_path}'.")
        filepath = f"./workspace/{db}/{str(id)}/{file_name}"
        colors = [ 
        ['#E34234', '#FF0000', '#D1001C'],# red
        ['#FFA500', '#FF7F50', '#FF4500'],# orange
        ['#FFFF00', '#FFEA00', '#FFD700'],# yellow
        ['#00FF00', '#32CD32', '#008000'], # green
        ['#1E90FF', '#4169E1', '#0000FF'], # blue
        ['#9370DB', '#8A2BE2', '#800080'], # purple
        ['#FF69B4', '#FFB6C1', '#FFC0CB'], # pink
        ['#A0522D', '#8B4513', '#A52A2A'], # brown
        ['#D3D3D3', '#A9A9A9', '#808080'], # grey
        ['#00FFFF', '#00CED1', '#20B2AA'], # cyan
        ['#2E8B57', '#43CD80', '#54FF9F'], # sea green
        ['#FF4500', '#FF6347', '#FF7F50'], # coral
        ['#483D8B', '#6A5ACD', '#836FFF'], # slate blue
        ['#556B2F', '#6E8B3D', '#9ACD32'], # olive
        ['#8B7D6B', '#BC8F8F', '#CDB79E'], # rosy brown
        ['#00CED1', '#48D1CC', '#AFEEEE'], # turquoise
        ['#8B7E66', '#CDAF95', '#FFDAB9'], # peach puff
        ['#8A0707', '#CD5C5C', '#FF6A6A'], # dark red
        ['#FF8C00', '#FFA54F', '#FFD39B'], # dark orange
        ['#CDCD00', '#EEE685', '#FFFFE0'], # light yellow
        ['#006400', '#548B54', '#7FFF00'], # dark green
        ['#00008B', '#1C86EE', '#87CEFA'], # dark blue
        ['#551A8B', '#9A32CD', '#BF3EFF'], # dark purple
        ['#FF1493', '#EE82EE', '#FFB5C5'], # deep pink
        ['#8B4513', '#A0522D', '#CD853F'], # dark brown
        ['#2F4F4F', '#696969', '#A9A9A9'], # dark grey
        ['#008B8B', '#48D1CC', '#AFEEEE'], # dark cyan
        ['#FF6347', '#FF8247', '#FFA07A'], # tomato
        ['#4682B4', '#5CACEE', '#B0E2FF'], # steel blue
        ['#8B008B', '#9B30FF', '#E066FF'] # magenta
        ]
        # fFlush()
        metadata_extractor(db,filepath,id)
        keyword_generator(db, id)
        # fFlush()
        mainpoints_generator(db, id)
        # fFlush()
        subpoints_generator(db,id)
        # fFlush()
        subpoints_extension(db,id)
        # fFlush()
        knowledge_density(db,id)
        # fFlush()
        generate_file_graph(db,id,colors)
        # fFlush()
        generate_points(db,id)
        # fFlush()
        html_generator(f"./workspace/{db}/{str(id)}/", f'mainpoints_{str(id)}.json', f"./{WORKDIR}/{db}/{str(id)}/")
        if file_name.endswith('.pdf'):
            shutil.copy2(f"./workspace/{db}/{str(id)}/{file_name}",f"./{WORKDIR}/{db}/{str(id)}/show.pdf")
        else :
            any2pdf(f"./workspace/{db}/{str(id)}",WORKDIR,db,str(id))
        id += 1
    # fFlush()
    generate_main_graph(db,colors)
    fFlush()



def generate_main_graph(db,colors):
    base_dir = f"./workspace/{db}"
    main_points = []
    res = {}
    res["name"] = db
    color_index = 0
    for subdir, dirs, files in os.walk(base_dir):
        for file in files:
            if file.startswith("mainpoints_") and file.endswith(".json"):
                file_path = os.path.join(subdir, file) 
                with open(file_path, 'r',encoding='utf-8') as f:
                    data = json.load(f)
                    main_points.append(data) 
    res["weight"] = 2.5
    res["sons"] = []
    num_each_file = int(10/len(main_points))+1
    for mainpoint in main_points:
        file_info = {}
        sub_color_index = 0
        file_info["name"] = mainpoint["keyword"]
        file_info["density"] = mainpoint["knowledgeDensity"]
        file_info["file"] = mainpoint["id"]
        file_info["color"] = colors[color_index][sub_color_index]
        sub_color_index += 1
        sorted_mainpoints = sorted(mainpoint["mainpoints"], key=lambda x: x.get('knowledgeDensity', 0), reverse=True)
        new_mainpoints = []
        for i in sorted_mainpoints:
            new_mainpoints.append({"name":i["name"],"density":i["knowledgeDensity"],"color":colors[color_index][sub_color_index],"file":mainpoint["id"],"page":i["pages"][0],"sons":[]})
        if len(new_mainpoints) >= num_each_file:
            file_info["sons"] = new_mainpoints[:num_each_file]
        else :
            file_info["sons"] = new_mainpoints
        res["sons"].append(file_info)
        color_index += 1
    origin_names = []
    for i in range(0,len(res['sons'])):
        for j in range(0,len(res['sons'][i]['sons'])):
            origin_names.append(res['sons'][i]['sons'][j]['name'])
    curtail_names = curtail(origin_names)
    index = 0
    for i in range(0,len(res['sons'])):
        for j in range(0,len(res['sons'][i]['sons'])):
            res['sons'][i]['sons'][j]['name'] = curtail_names[index]
            index += 1

    subpoints_list = []
    for i in res["sons"]:
        subpoints_list.extend(i["sons"])
    subpoints_list.sort(key=lambda x: x["density"], reverse=False)
    n = len(subpoints_list)
    num_middle = int(np.ceil(2 * n / 3))  
    num_sides = n - num_middle 
    num_left = num_sides // 2  
    num_right = n - num_left - num_middle  
    samples_left = np.linspace(0.1, 1/3, num_left, endpoint=False)
    samples_middle = np.linspace(1/3, 2/3, num_middle, endpoint=False)
    samples_right = np.linspace(2/3, 0.9, num_right, endpoint=True)
    sample = np.sort(np.concatenate((samples_left, samples_middle, samples_right)))
    for j, new_value in zip(subpoints_list, sample):
        j["weight"] = new_value   
    subpoints_list = []
    for i in res["sons"]:
        subpoints_list.append(i)
    subpoints_list.sort(key=lambda x: x["density"], reverse=False)
    n = len(subpoints_list)
    num_middle = int(np.ceil(2 * n / 3))  
    num_sides = n - num_middle 
    num_left = num_sides // 2  
    num_right = n - num_left - num_middle  
    samples_left = np.linspace(1, 4/3, num_left, endpoint=False)
    samples_middle = np.linspace(4/3, 5/3, num_middle, endpoint=False)
    samples_right = np.linspace(5/3, 2, num_right, endpoint=True)
    sample = np.sort(np.concatenate((samples_left, samples_middle, samples_right)))
    for j, new_value in zip(subpoints_list, sample):
        j["weight"] = new_value 
         
    save_path = f"./{WORKDIR}/{db}/main_graph.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)   
        

                    
def generate_file_graph(db,id,colors):
    color_index = 0
    res = {}
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        main_points = json.load(file)
    res["name"] = main_points["keyword"]
    res["density"] = main_points["knowledgeDensity"]
    res["weight"] = 2.5
    res["file"] = main_points["id"]
    res["sons"] = []
    num_each_file = int(10/len(main_points["mainpoints"]))+1
    for mainpoint in main_points["mainpoints"]:
        sub_color_index = 0
        file_info = {}
        file_info["name"] = mainpoint["name"]
        file_info["density"] = mainpoint["knowledgeDensity"]
        file_info["color"] = colors[color_index][sub_color_index]
        sub_color_index += 1
        file_info["file"] = main_points["id"]
        file_info["page"] = mainpoint["pages"][0]
        sorted_subpoints = sorted(mainpoint["subpoints"], key=lambda x: x.get('knowledgeDensity', 0), reverse=True)
        new_subpoints = []
        for i in sorted_subpoints:
            new_subpoints.append({"name":i["name"],"density":i["knowledgeDensity"],"weight":i["weight"],"color":colors[color_index][sub_color_index],"file":main_points["id"],"page":i["pages"][0],"sons":[]})
        if len(new_subpoints) >= num_each_file:
            file_info["sons"] = new_subpoints[:num_each_file]
        else :
            file_info["sons"] = new_subpoints
        res["sons"].append(file_info)
        color_index += 1
        
    subpoints_list = []
    for i in res["sons"]:
        subpoints_list.append(i)
    subpoints_list.sort(key=lambda x: x["density"], reverse=False)
    n = len(subpoints_list)
    num_middle = int(np.ceil(2 * n / 3))  
    num_sides = n - num_middle 
    num_left = num_sides // 2  
    num_right = n - num_left - num_middle  
    samples_left = np.linspace(1.0, 4/3, num_left, endpoint=False)
    samples_middle = np.linspace(4/3, 5/3, num_middle, endpoint=False)
    samples_right = np.linspace(5/3, 2, num_right, endpoint=True)
    sample = np.sort(np.concatenate((samples_left, samples_middle, samples_right)))
    for j, new_value in zip(subpoints_list, sample):
        j["weight"] = new_value 
    

    origin_names = []
    for i in range(0,len(res['sons'])):
        origin_names.append(res['sons'][i]["name"])
        for j in range(0,len(res['sons'][i]['sons'])):
            origin_names.append(res['sons'][i]['sons'][j]['name'])
    print(origin_names)
    curtail_names = curtail(origin_names)
    print(curtail_names)     
    index = 0
    for i in range(0,len(res['sons'])):
        res['sons'][i]['name'] = curtail_names[index]
        index += 1
        for j in range(0,len(res['sons'][i]['sons'])):
            res['sons'][i]['sons'][j]['name'] = curtail_names[index]
            index += 1  
      
    save_path = f"./{WORKDIR}/{db}/{id}/file_graph.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)  

def generate_points(db,id):
    if not os.path.exists(f"./{WORKDIR}/{db}/{str(id)}/html"):
        os.makedirs(f"./{WORKDIR}/{db}/{str(id)}/html")
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        main_points = json.load(file)
    res = {}
    res["keyword"] = main_points["keyword"]
    res["mainpoints"] = []
    for mainpoint in main_points["mainpoints"]:
        new_mainpoint = {}
        new_mainpoint["name"] = mainpoint["name"]
        new_mainpoint["from_page"] = mainpoint["pages"][0]
        new_mainpoint["to_page"] = mainpoint["pages"][1]
        new_mainpoint["subpoints"] = []
        for i in mainpoint["subpoints"]:
            new_mainpoint["subpoints"].append({"name":i["name"],"from_page":i["pages"][0],"to_page":i["pages"][1],"filename": f"{i['name']}.pdf"}) 
        res["mainpoints"].append(new_mainpoint)
    save_path = f"./{WORKDIR}/{db}/{id}/points.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)  

def bConversation(db: str, context) :
    print("CALL")
    print(db)
    print(context)
    question = ""
    background = ""
    log = ""
    page = ""
    for i in range(len(context)):
        if context[i][3] is not None:
            metadata_path = f"./workspace/{db}/{str(context[i][0])}/metadata_{str(context[i][0])}.json"
            with open(metadata_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
            content = ""
            content += f"\nHere is one question of the user:{context[i][2]}"
            content += f"\nYour answer is {context[i][3]} \n"
            log += content
        else :
            metadata_path = f"./workspace/{db}/{str(context[i][0])}/metadata_{str(context[i][0])}.json"
            with open(metadata_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
            background = json.dumps(metadata, indent=4)
            question = context[i][2]
            page = str(context[i][1])
            
    prompt = "Suppose you are study assistant whose name is 'Study Compass'.\n"
    prompt += log
    prompt += "\n The content above is the log of the user's questions and your corresponding answers.(You can ignore if it is blank).\n"
    prompt += background
    prompt += f"\n The content above is the background information of the question.The question is mainly based on the content in page {page}. So you need to pay more attention.\n"
    prompt += question
    prompt += "\nPlease based on your previous answers and background information,answer the question above.Your answer should  be in Chinese."
    res = query_gpt4(prompt)
    return res   

# TreeNode ->  TreeRoot 
#    |            +-> DatabaseTree
#    +---->  KnowledgeDatabase
#    +-->  FileSlot
#    +->  ...

class TreeNode: pass

# class ...(TreeNode):
#     def construct_node(self):
#         self.build_node('end', self.name)

#     def after_construction(self):
#         pass

#     def onclick(self):
#         pass

class TreeNode:
    # name: string
    # father: TreeNode
    # dir: string
    # sons: Dict<id, TreeNode>
    # ids: Dict<name, id>
    def __init__(self, name, ext=None):
        self.sons = dict()
        self.ids = dict()
        self.name = name
        self.ext = ext
    
    # virtual
    def construct_node(self):
        self.build_node('end', self.name)

    # virtual
    def after_construction(self):
        pass

    # virtual
    def onclick(self):
        print("Click on item: ", self.name)

    # virtual
    def get_dir(self) -> str:
        return self.father.dir

    # 构建节点辅助函数
    def build_node(self, index, text, icon=None):
        if icon is None:
            self.item_id = self.root.tree.insert(self.father.item_id, index, text=text)
        else:
            self.item_id = self.root.tree.insert(self.father.item_id, index, text=text, image=self.root.icons[icon])

    # 添加子节点
    def add_son(self, node: TreeNode):
        node.root = self.root
        node.father = self
        node.dir = node.get_dir()
        node.construct_node()
        self.ids[node.name] = node.item_id
        self.sons[node.item_id] = node
        node.after_construction()
        return node.item_id

    # 获取子节点
    def get_son_by_name(self, name):
        return self.sons[self.ids[name]]

    def onclick_rev(self, path):
        if len(path) == 0:
            self.onclick()
        elif path[0] in self.sons:
            self.sons[path[0]].onclick_rev(path[1:])
        else:
            print("Err", path)

class TreeRoot(TreeNode):
    def __init__(self, master):
        self.tree = ttk.Treeview(master)
        self.tree.bind('<Double-1>', self.onclick_root)

        self.root = self
        self.item_id = ''
        self.sons = dict()
        self.ids = dict()

    def onclick_root(self, event):
        item_id = self.tree.focus()
        path = []
        while item_id:
            path.append(item_id)
            item_id = self.tree.parent(item_id)
        path.reverse()
        self.onclick_rev(path)

    def clear(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self.sons = dict()
        self.ids = dict()

class MainGraph(TreeNode):
    def construct_node(self):
        self.build_node('end', '主思维导图', 'graph')

    def onclick(self):
        g=self.root.father.sw.switch('graph0')
        g.load_file(self.dir)
        g.db_name=self.father.name

    def get_dir(self) -> str:
        return self.father.dir + 'main_graph.json'
    
class FileGraph(TreeNode):
    def construct_node(self):
        self.build_node('end', '文件思维导图', 'graph')

    def onclick(self):
        self.root.father.set_status(self.father.father.father.name, int(self.father.name), 0)
        self.root.father.sw.switch('graph')

    def get_dir(self) -> str:
        return self.father.dir + 'file_graph.json'
    
class SubPoint(TreeNode):
    def construct_node(self):
        self.html_file_name = self.ext['filename']
        self.from_page = self.ext['from_page']
        self.to_page = self.ext['to_page']
        self.build_node('end', self.ext['name'], 'lightbulb')

        # print(self.get_db_name(), self.get_file_id())
        for i in range(self.from_page,self.to_page+1):
            self.root.father.sw.get('html').add_dict((self.get_db_name(), self.get_file_id(), i),self.get_dir()+'/'+self.html_file_name)

    def onclick(self):
        self.root.father.set_status(self.get_db_name(), self.get_file_id(), self.from_page)
        self.root.father.sw.switch('html')

    def get_db_name(self):
        return self.father.father.father.father.name
    def get_file_id(self):
        return int(self.father.father.name)
        
    def get_dir(self) -> str:
        return self.father.dir + 'html/'
        
class MainPoint(TreeNode):
    def construct_node(self):
        self.build_node('end', self.ext['name'], 'lightbulb')

    def after_construction(self):
        for i, subpoint in enumerate(self.ext["subpoints"]):
            self.add_son(SubPoint(f'S{i}', subpoint))
            
    
class FileSlot(TreeNode):
    def construct_node(self):
        if os.path.exists(self.dir + 'points.json'):
            self.points = json.loads(open(self.dir + 'points.json', encoding='utf-8').read())
        else:
            self.points = { "keyword": "未知文件", "mainpoints": [] }
        self.build_node(1, self.points.get('keyword', self.name), 'file')

    def get_dir(self) -> str:
        return self.father.dir + self.name + '/'
    
    def after_construction(self):
        self.add_son(FileGraph('graph'))
        for i, mainpoint in enumerate(self.points["mainpoints"]):
            self.add_son(MainPoint(f'M{i}', mainpoint))
    
    def onclick(self):
        self.root.father.set_status(self.father.father.name, int(self.name), 0)
        self.root.father.sw.switch('pdf')

class AddFileButton(TreeNode):
    def construct_node(self):
        self.build_node(0, '添加文件', 'plus')

    def onclick(self):
        entry_str = filedialog.askopenfilename(filetypes=[
            ("PPT", ["pptx"]),
            ("PDF", ["pdf"]),
            ("DOC", ["docx"]),
            ])
        if len(entry_str) == 0:
            return
        
        thread=threading.Thread(target=lambda: bAddFiles(self.father.father.name, [entry_str]))
        thread.start()

class FileList(TreeNode):
    def after_construction(self):
        self.add_son(AddFileButton('<add_file>'))
        for path in os.listdir(self.dir):
            if path != 'conv' and os.path.isdir(os.path.join(self.dir, path)):
                self.add_son(FileSlot(path))
        
    def construct_node(self):
        self.build_node('end', '资料库', 'disk')

class ConversationSlot(TreeNode):
    def construct_node(self):
        # print("construct called")
        self.build_node(0, json.loads(open(self.get_dir(),encoding='utf-8').read())['name'], 'clock')

    def onclick(self):
        app.sw.switch('dialog').load_file(self.get_dir())
        app.set_status(self.father.father.name, None,None)

    def get_dir(self) -> str:
        return self.father.dir + self.name

class AddConversationButton(TreeNode):
    def construct_node(self):
        self.build_node(0, '添加问答', 'plus')

    def onclick(self):
        self.father.new_conv()

class ConversationList(TreeNode):
    def construct_node(self):
        self.build_node('end', '问答记录', 'clock')

    def after_construction(self):
        self.add_son(AddConversationButton('<add_conv>'))
        dir=self.get_dir()
        if not os.path.exists(dir): os.mkdir(dir)
        for file in os.listdir(dir):
            self.add_son(ConversationSlot(file))
        self.cnt=len(os.listdir(dir))

    def new_conv(self):
        new_filename=f'{self.cnt}.json'
        self.cnt+=1
        open(self.get_dir()+new_filename,encoding='utf-8',mode='w').write(f'{{"name":"未开启的对话", "db":"{self.father.name}","his":[]}}')
        self.add_son(ConversationSlot(new_filename))

    def get_dir(self) -> str:
        return self.father.dir + 'conv/'

class KnowledgeDatabase(TreeNode):
    def after_construction(self):
        self.add_son(MainGraph('mg'))
        self.add_son(FileList('fs'))
        self.add_son(ConversationList('cl'))

    def construct_node(self):
        self.build_node(1, self.name, 'database')

    def get_dir(self) -> str:
        return self.father.dir + self.name + '/'


class AddKnowledgeDatabaseButton(TreeNode):
    def construct_node(self):
        self.build_node(0, '添加知识库', 'plus')

    def onclick(self):
        entry_str=simpledialog.askstring(title='创建知识库',prompt='输入知识库名')
        if entry_str is None:
            return
        if entry_str in self.father.ids:
            messagebox.showerror(title='错误',message='知识库已存在')
        else:
            bCreateDatabase(entry_str)
            
class DatabaseTree(TreeRoot):
    def __init__(self, master, father):
        super().__init__(master)
        self.icons = {
            "plus": get_font_icon("plus", style="solid", height=16, fg="green"),
            "disk": get_font_icon("floppy-disk", style="solid", height=16, fg="grey"),
            "database": get_font_icon("database", style="solid", height=16, fg="blue"),
            "file": get_font_icon("file", style="regular", height=16, fg="black"),
            "graph": get_font_icon("diagram-project", style="solid", height=16, fg="black"),
            "clock": get_font_icon("clock", style="regular", height=16, fg="black"),
            "lightbulb": get_font_icon("lightbulb", style="solid", height=16, fg="orange"),
        }

        self.father = father
        self.dir = WORKDIR
        
    def construct_node(self):
        self.add_son(AddKnowledgeDatabaseButton('<add>'))
        for db_name in os.listdir(self.dir):
            if db_name != 'workspace':
                self.add_son(KnowledgeDatabase(db_name))

class AutoImageView(tk.Label):
    def __init__(self, master):
        super().__init__(master)
        self.origin_img=Image.Image()

        self.bind("<Configure>", self.resize_image)

    def set_img(self, img: Image.Image):
        self.origin_img = img
        self.resize_image()

    def resize_image(self, event=None):
        new_width = self.winfo_width()
        new_height = self.winfo_height()

        # 计算等比例缩放后的图片大小
        original_width, original_height = self.origin_img.size
        ratio = min(new_width/original_width, new_height/original_height)
        new_size = int(original_width * ratio), int(original_height * ratio)

        # 防止窗口最小化时出错
        if new_size[0] > 0 and new_size[1] > 0:
            self.image = self.origin_img.resize(new_size, Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.config(image=self.photo)

class PdfReader(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        # 当前PDF文档和页面
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0

        self.buttonCanvas = tk.Canvas(self)
        self.buttonCanvas.pack()
        self.buttonCanvas.config(highlightthickness=0)

        self.style = ttk.Style()
        self.style.configure("Custom.TButton", foreground="black", background="grey",
                            bordercolor='black', padding=[3,1], borderwidth=5, relief=tk.SUNKEN, font=('SimHei', 11))

        self.prev_button = ttk.Button(self.buttonCanvas, text=" << 前一页", command=self.show_prev_page, style="Custom.TButton")
        self.prev_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = ttk.Button(self.buttonCanvas, text="后一页 >>", command=self.show_next_page, style="Custom.TButton")
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)


        # 创建标签用于显示PDF页面图像
        self.image_label = AutoImageView(self)
        self.image_label.pack(side=tk.TOP,fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.path = None
        self.open_path(None)

    def open_path(self, path):
        if path is None or not os.path.exists(path): 
            print("PDF文件不存在: ", path)
            path='./src/nop.pdf'
        if self.path==path: return

        self.pdf_document = fitz.open(path)
        self.path = path
        self.total_pages = len(self.pdf_document)
        self.current_page = 0
        self.show_page()

    def show_page(self):
        if self.pdf_document:
            page = self.pdf_document.load_page(self.current_page)

            # 将PDF页面转换为图像
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # 在Tkinter窗口中显示图像
            # photo = ImageTk.PhotoImage(image=img)
            # self.image_label.config(image=photo)
            # self.image_label.image = photo  # 保持对图像的引用
            self.image_label.set_img(img)

    def show_prev_page(self):
        if self.current_page > 0:
            app.set_status(None, None, self.current_page-1)

    def show_next_page(self):
        if self.current_page < self.total_pages - 1:
            app.set_status(None, None, self.current_page+1)
    
    def set_page(self, page: int):
        self.current_page = page
        if self.current_page < 0: self.current_page = 0
        if self.current_page >= self.total_pages: self.current_page = self.total_pages - 1
        self.show_page()
            
    def remake(self, master):
        new = PdfReader(master)
        new.open_path(self.path)
        new.set_page(self.current_page)
        self.destroy()
        return new

    def set_status(self, state: (str, int, int)):
        dbname, file, page = state
        dir = f'{WORKDIR}{dbname}/{file}/show.pdf'
        self.open_path(dir)
        self.set_page(page)

class SinglePagePdfReader(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.image_label = AutoImageView(self)
        self.image_label.pack(side=tk.TOP,fill=tk.BOTH, padx=10, pady=10, expand=True)

        self.point_ind={}
        self.filename=None
        self.load_file(None)

    def load_file(self, filename):
        if filename is None or not os.path.exists(filename):
            print("PDF文件不存在: ", filename)
            filename='./src/nop.pdf'
        if self.filename==filename: return
        self.filename=filename

        pdf_document = fitz.open(filename)
        page = pdf_document.load_page(0)

        # 将PDF页面转换为图像
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 在Tkinter窗口中显示图像
        # photo = ImageTk.PhotoImage(image=img)
        # self.image_label.config(image=photo)
        # self.image_label.image = photo  # 保持对图像的引用
        self.image_label.set_img(img)

    def set_status(self, state: (str, int, int)):
        if state in self.point_ind:
            self.load_file(self.point_ind[state])
        else:
            # print(self.point_ind)
            print("Not found: ", state)
        
    def add_dict(self, state, file_name):
        self.point_ind[state] = file_name
        # print(state,file_name, self.point_ind)

    def remake(self, master):
        new = SinglePagePdfReader(master)
        new.load_file(self.filename)
        new.point_ind=self.point_ind
        self.destroy()
        return new
    
class HtmlWidget(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.html_display = HTMLLabel(self, html="")
        self.html_display.pack(fill="both", expand=True)
        self.filename=''

    def load_file(self, filename):
        self.filename=filename
        if os.path.exists(filename):
            self.html_display.set_html(open(filename,encoding='utf-8').read())
        else:
            self.html_display.set_html("<h1>文件不存在</h1>")

    def remake(self, master):
        new = HtmlWidget(master)
        new.load_file(self.filename)
        self.destroy()
        return new
        
class HangingSign(tk.Label):
    def __init__(self, master):
        super().__init__(master)
        self.text=''

    def set_text(self, text: str):
        self.text=text
        self.config(text=text)

    def remake(self, master):
        new = HangingSign(master)
        new.set_text(self.text)
        self.destroy()
        return new
    
    def set_status(self, state: (str, int, int)):
        dbname, file, page = state
        self.set_text(f'({dbname},{file},{page})')

def is_chinese_char(ch) -> bool:
    if '\u4e00' <= ch <= '\u9fff':
        return True
    elif '\u3400' <= ch <= '\u4dbf':
        return True
    else:
        return False

def lineMeasurement(text):
    totalChars = 0
    charCnt = 0
    lineCnt = 1
    for ch in text:
        if is_chinese_char(ch):
            charCnt += 2
            totalChars += 2
        else:
            charCnt += 1
            totalChars += 1
        if charCnt >= 70 or ch == '\n':
            lineCnt += 1
            charCnt = 0
    return totalChars, lineCnt


# 右侧一组回话的内容
class ConversationCanvas(tk.Canvas):
    def __init__(self, window, master, text, userType, color, outline, length, **kwargs):
        super().__init__(master, **kwargs, height=length)
        self.window = window
        self.text = text
        self.color = color
        self.outline = outline
        self.usertype = userType
        self.height = length
        self.create()
        
    def create(self):
        user = Image.open("./src/resources/user.png")
        robot = Image.open("./src/resources/robot.png")
        if not self.usertype:
            self.avatar = ImageTk.PhotoImage(user)
        else:
            self.avatar = ImageTk.PhotoImage(robot)

        create_arc_rect(self, 5, 5, 800, self.height, 25, self.color, self.outline)
        # 在画布上添加图片
        self.create_image(10, 10, anchor="nw", image=self.avatar)  # 参数为图片放置的坐标

        self.create_text(60, 20, text=self.text, anchor="nw", font=('黑体', 15), width=720)

def answer(content):
    # client = openai.OpenAI()
    # completion = client.chat.completions.create(model="gpt-4-1106-preview", messages=[{"role": "user", "content": content}],temperature=0.7)
    # return completion.choices[0].message.content
    return '没接入'

# 创建圆角矩形区域
def create_arc_rect(canvas, x1, y1, x2, y2, radius, color="", outline=""):
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]

    region = canvas.create_polygon(points, fill=color, smooth=True, outline=outline, width=2)

    return region

class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None

    def show_tip(self, tip_text):
        "Display text in tooltip window"
        if self.tip_window or not tip_text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")  # 获取部件的位置
        x = x + self.widget.winfo_rootx() + 25  # 计算tooltip的位置
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)  # 去除窗口边框
        tw.wm_geometry("+%d+%d" % (x, y))  # 设置tooltip的位置
        label = tk.Label(tw, text=tip_text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("simHei", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()
        
class DialogList(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.path=None
        self.create()

    def load_file(self, path):
        # print("load called")
        if self.path==path: return
        self.path=path
        if not os.path.exists(path):
            self.text.config(text=f'"{path}" 不存在')
            return

        self.json=json.load(open(self.path,encoding='utf-8'))
        self.totalHeight = 0
        # 清空原本所有组件
        for widget in self.conversationFrame.winfo_children():
            widget.destroy()
        # 创建新的组件
        if (hasattr(self, 'json')):
            for conv in self.json["his"]:
                _, _, userText, machineText = conv[0], conv[1], conv[2], conv[3]
                type = "user"
                _, lines = lineMeasurement(userText)
                conCV = ConversationCanvas(self, self.conversationFrame, userText, 0 if type == "user" else 1,
                                                            "#FFDF92" if type == "user" else "#B5D3D9",
                                                            "#DD6C4C" if type == "user" else "#14365F",
                                                            width=800, length=max(50, 20 + 18 * lines + 35))
                self.totalHeight += max(50, 20 + 18 * lines + 35)
                conCV.pack()
                type = "machine"
                _, lines = lineMeasurement(machineText)
                conCV = ConversationCanvas(self, self.conversationFrame, machineText, 0 if type == "user" else 1,
                                                            "#FFDF92" if type == "user" else "#B5D3D9",
                                                            "#DD6C4C" if type == "user" else "#14365F",
                                                            width=800, length=max(50, 20 + 18 * lines + 35))
                self.totalHeight += max(50, 20 + 18 * lines + 35)
                conCV.pack()
        self.conversationCanvas.configure(yscrollcommand=self.scrollbar.set, scrollregion=tuple([0, 0, 806, self.totalHeight]))
        self.redraw()

    def on_enter(self, event):
        db, f, p = app.get_status()
        if f is None or p is None or not hasattr(self, "json"):
            return
        ask=self.input.get()
        history = []
        for his in self.json["his"]:
            history.append(his)
        history.append([f, p, ask, None])
        def async_conversation(db, history):
            ans = bConversation(self.json["db"], history)
            type = "user"
            _, lines = lineMeasurement(ask)
            conCV = ConversationCanvas(self, self.conversationFrame, ask, 0 if type == "user" else 1,
                                                        "#FFDF92" if type == "user" else "#B5D3D9",
                                                        "#DD6C4C" if type == "user" else "#14365F",
                                                        width=800, length=max(50, 20 + 18 * lines + 35))
            self.totalHeight += max(50, 20 + 18 * lines + 35)
            conCV.pack()
            type = "machine"
            _, lines = lineMeasurement(ans)
            conCV = ConversationCanvas(self, self.conversationFrame, ans, 0 if type == "user" else 1,
                                                        "#FFDF92" if type == "user" else "#B5D3D9",
                                                        "#DD6C4C" if type == "user" else "#14365F",
                                                        width=800, length=max(50, 20 + 18 * lines + 35))
            self.totalHeight += max(50, 20 + 18 * lines + 35)
            conCV.pack()
            self.conversationCanvas.configure(yscrollcommand=self.scrollbar.set, scrollregion=tuple([0, 0, 806, self.totalHeight]))
            self.json['his'].append([f,p,ask,ans])
            self.json['name'] = ask[:8] + "..." if len(ask) >= 8 else ask 
            json.dump(self.json,open(self.path,encoding='utf-8',mode='w'))
            self.input.delete(0, tk.END)
            self.redraw()
        thread = threading.Thread(target=async_conversation, args=(self.json['db'], history))
        thread.start()

    def clear(self, event):
        self.totalHeight = 0
        # 清空原本所有组件
        for widget in self.conversationFrame.winfo_children():
            widget.destroy()
        self.json['his'].clear()
        self.json['name'] = "未保存的对话"
        json.dump(self.json,open(self.path,encoding='utf-8',mode='w'))

    def redraw(self):
        pass

    def remake(self, master):
        new = DialogList(master)
        new.load_file(self.path)
        self.destroy()
        return new
    
    def set_status(self, state: (str, int, int)):
        dbname, file, page = state
        if dbname!=self.json['db']: self.load_file('')

    def input_enter(self, event):
        db, f, p = app.get_status()
        if f is None or p is None or not hasattr(self, "json"):
            self.input.config(state="disabled")
        else:
            self.input.config(state="normal")
        self.tooltip.show_tip("请在选中相应页面和文件后输入，一次输入一条")

    def create(self):
        # 总体区域架构
        # print("create called")
        self.conversation = tk.Frame(self)
        self.conversation.pack(side=tk.LEFT, fill="both", padx=0, pady=0)
        # 区域上层canvas用于承载Frame
        self.conversationCanvas = tk.Canvas(self.conversation, width=800)
        self.conversationCanvas.pack(side=tk.TOP, padx=0, pady=0)
        # Frame存放所有对话
        self.conversationFrame = tk.Frame(self.conversation)
        self.conversationCanvas.create_window((0, 0), window=self.conversationFrame, anchor="nw")
        # 右侧滚动条
        self.scrollbar = tk.Scrollbar(self, command=self.conversationCanvas.yview)
        self.scrollbar.pack(side=tk.LEFT, fill="y")
        # 配置滚动区域
        self.conversationCanvas.configure(yscrollcommand=self.scrollbar.set, scrollregion=self.conversationCanvas.bbox("all"))
        # 输入框及发送的Frame
        self.inputFrame = tk.Canvas(self.conversation)
        self.inputFrame.pack(side=tk.BOTTOM, fill="both")
        self.inputFrame.config(highlightthickness=0)
        self.inputRegion = create_arc_rect(self.inputFrame, 5, 17.5, 720, 55, 10, "#B4BFD0", '#8694AD')
        # 输入框
        self.input = tk.Entry(self.inputFrame, width=100)
        self.input.pack(side=tk.LEFT, padx=10, pady=0)

        self.tooltip = ToolTip(self.input)
        # 为Entry控件添加鼠标进入和离开事件，以显示和隐藏tooltip
        self.input.bind('<Enter>', self.input_enter)
        self.input.bind('<Leave>', lambda e: self.tooltip.hide_tip())
        # 工具栏
        self.tools = tk.Canvas(self.inputFrame, width=130, height=50)
        self.tools.pack(side=tk.LEFT, padx=0, pady=10)
        # 一些图片
        chat = Image.open("./src/resources/chat.png")
        self.chatImage = ImageTk.PhotoImage(chat)

        delete = Image.open("./src/resources/delete.png")
        self.deleteImage = ImageTk.PhotoImage(delete)

        refresh = Image.open("./src/resources/refresh.png")
        self.refreshImage = ImageTk.PhotoImage(refresh)

        self.sendRegion = create_arc_rect(self.tools, 12, 12, 45, 45, 7.5, "#E9F5A1", '#5D887B')
        self.tools.create_image(10, 10, anchor="nw", image=self.chatImage)
        self.sendButton = self.tools.create_rectangle(12.5, 12.5, 45, 45, tags="", outline="", fill="")
        self.tools.tag_bind(self.sendButton, "<Button-1>", self.on_enter)
        # 创建删除按钮
        self.tools.create_image(50, 10, anchor="nw", image=self.deleteImage)
        self.deleteButton = self.tools.create_rectangle(50, 10, 85, 45, tags="", outline="", fill="")
        # TODO 删除对话
        # self.tools.tag_bind(self.deleteButton, "<Button-1>", self.on_enter)
        # 创建清空按钮
        self.tools.create_image(90, 10, anchor="nw", image=self.refreshImage)
        self.refreshButton = self.tools.create_rectangle(90, 10, 125, 45, tags="", outline="", fill="")
        self.tools.tag_bind(self.refreshButton, "<Button-1>", self.clear)

def devide_str(s: str):
    l = len(s)
    if l < 6: return s
    else: return '\n'.join([s[:l//2],s[l//2:]])

# 目前有大量bug
# 1. 关闭窗口不能正常退出
# 2. 不能显示中文
# 3. 移动到哪个节点上判断逻辑有问题
# 4. 应该采用固定坐标轴
class GraphWidget(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.dragging_node = None

        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_move)

        self.canvas_widget = FigureCanvasTkAgg(self.fig, self).get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(self, text="请打开思维导图", justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "20", "normal"))
        self.label.pack(fill=tk.BOTH, expand=False)

        self.filename=None
        self.load_file()
        
        
    def load_file(self, filename=None):
        if filename is not None and self.filename==filename: return
        self.filename=filename
        self.node_cnt = 0
        self.org_graph = dict()
        self.labels = dict()
        self.undivided_labels = dict()
        self.links = []
        self.densities = []
        self.colors = []
        self.sizes = []
        self.db_name=None

        if filename is not None and os.path.exists(filename):
            self.parse_conf(json.loads(open(filename,encoding='utf-8').read()))
            self.graph = nx.Graph(self.org_graph)
        else:
            self.graph = nx.Graph()

        self.set_default_pos()
        self.draw()

    def map_weight_to_size(self, weight):
        # return weight**0.25 * 1500
        return weight * 1500 + 500
        
    def parse_conf(self, conf) -> int:
        id = self.node_cnt
        self.node_cnt += 1

        self.undivided_labels[id] = conf['name']
        self.labels[id] = devide_str(conf['name'])
        self.links.append((conf.get('file', -1), conf.get('page', 0)))
        self.colors.append(conf.get('color', '#1f78b4'))
        self.densities.append(conf.get('density', float('nan')))
        self.sizes.append(self.map_weight_to_size(conf.get('weight', 1.0)))

        son_list = []
        for cf in conf['sons']:
            son_list.append(self.parse_conf(cf))
        self.org_graph[id] = son_list

        return id
    
    def set_default_pos(self):
        self.pos = nx.spring_layout(self.graph)
    
    def draw(self):
        self.ax.clear()
        nx.draw(self.graph, self.pos, 
                with_labels=True,
                nodelist=list(range(self.node_cnt)),
                labels=self.labels,
                node_size=self.sizes,
                node_color=self.colors,
                font_family='SimHei',
                ax=self.ax,
                )
        self.fig.canvas.draw()

    def find_pointed_node(self, event):
        for node, node_pos in self.pos.items():
            distance = ((event.xdata - node_pos[0])**2 + (event.ydata - node_pos[1])**2)**0.5
            if distance < 0.1:  # 鼠标在节点附近
                return node
        return None
            
    def on_click(self, event):
        if event.xdata is None or event.ydata is None: return None
        node = self.find_pointed_node(event)
        if node is None: return

        if event.dblclick:
            self.on_dbclick(node)
        else:
            self.dragging_node = node

    def on_release(self, event):
        self.dragging_node = None

    def on_move(self, event):
        if event.xdata is None or event.ydata is None: return
        if self.dragging_node is not None:
            # dragging
            self.pos[self.dragging_node] = (event.xdata, event.ydata)
            self.draw()
        else:
            # normal pointed
            node = self.find_pointed_node(event)
            if node is None: self.showtip("请点击节点")
            else: self.showtip(self.get_show_info(node))

    def get_show_info(self, id):
        return f'知识点: "{self.undivided_labels[id]}" 知识密度: {self.densities[id]:.2f}'

    def showtip(self, text):
        self.label.config(text=text)

    def remake(self, master):
        new = GraphWidget(master)
        new.load_file(self.filename)
        new.db_name=self.db_name
        self.destroy()
        return new

    def on_dbclick(self, node):
        print("Jumping to: ", self.links[node])
        file, page = self.links[node]
        if file==-1: return
        app.set_status(self.db_name, file, page)
        app.sw.switch('html')

    def set_status(self, state: (str, int, int)):
        dbname, file, page = state
        self.db_name=dbname
        if file==-1:
            self.load_file(f'{WORKDIR}{dbname}/main_graph.json')
        else:
            self.load_file(f'{WORKDIR}{dbname}/{file}/file_graph.json')
        # pass

class SwitchWidget(tk.Frame):
    def __init__(self, master):

        super().__init__(master)
        self.style = ttk.Style()
        self.style.configure("Custom.TButton", foreground="black", background="black", padding=[3,1], borderwidth=5, relief=tk.SUNKEN, font=('SimHei', 11))
        self.detach_button = ttk.Button(self, text="使用新窗口打开当前标签页", command=self.detach, style="Custom.TButton")
        self.detach_button.pack(side=tk.TOP)
        # 选择一个主题
        self.style.theme_use('winnative')  # 或者你可以选择 'clam', 'alt', 'classic' 等
        self.style.configure('CustomNotebook.TNotebook.Tab', padding=[5, 2], font=('SimHei', 11), borderwidth=5)
        self.style.map('CustomNotebook.TNotebook.Tab',
                background=[('selected', '#9cb3d4')],  # 选中Tab的背景颜色
                foreground=[('selected', 'black')])  # 选中Tab的前景颜色（即字体颜色）
        self.tabs = ttk.Notebook(self, style="CustomNotebook.TNotebook")
        self.tabs.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.names = dict()
        self.widgets = dict()
        self.texts = dict()
        self.in_tabs = dict()

    def add(self, name, widget, text):
        self.names[widget] = name
        self.widgets[name] = widget
        self.texts[name] = text
        self.in_tabs[name] = True
        self.tabs.add(widget, text=text)

    def get(self, name):
        return self.widgets[name]

    def switch(self, name):
        w = self.widgets[name]
        if self.in_tabs[name]: self.tabs.select(w)
        return w

    def detach(self):
        name = self.names[self.tabs.nametowidget(self.tabs.select())]
        print(name)

        self.in_tabs[name] = False
        w = self.widgets[name]
        new_window = tk.Toplevel(self)
        new_window.title(self.texts[name])
        new_window.geometry("1200x800")
        new_window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(new_window, name))
        w = w.remake(new_window)
        self.widgets[name] = w
        self.names[w]=name
        w.pack(fill=tk.BOTH, expand=True)
        # w.pack_forget()
        # w.pack(in_=new_window)

    def onclose(self, window, name):
        self.in_tabs[name] = True
        w = self.widgets[name]
        w = w.remake(self)
        self.widgets[name] = w
        self.names[w]=name
        self.tabs.add(w, text=self.texts[name])
        window.destroy()

# State:
# db: str
# file: int
# page: int
# tab: Html / Graph / Conv / Sign
# 
class App:
    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.title("Study Compass v0.2")
        # self.main_window.geometry('1920x1080+10+10')
        self.main_window.iconbitmap('./src/favicon.ico')

        # 测试按钮
        # self.flush_button = tk.Button(self.main_window, text="模拟flush", command=self.flush)
        # self.flush_button.pack(side=tk.TOP)

        # 
        self.paned_window = ttk.PanedWindow(self.main_window, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        # 左侧树形
        self.db = DatabaseTree(self.paned_window, self)
        # self.db.tree.pack(side=tk.LEFT, fill=tk.Y)
        self.paned_window.add(self.db.tree, weight=1)

        # 右侧页面
        self.sw = SwitchWidget(self.paned_window)
        # self.sw.pack(side=tk.LEFT, fill=tk.Y, expand=True)
        self.paned_window.add(self.sw, weight=1)

        self.sw.add('sign', HangingSign(self.sw), '提示器')
        self.sw.add('html', SinglePagePdfReader(self.sw), '知识点阅读器')
        self.sw.add('graph0', GraphWidget(self.sw), '库思维导图')
        self.sw.add('graph', GraphWidget(self.sw), '文件思维导图')
        self.sw.add('pdf', PdfReader(self.sw), 'PDF阅读器')
        self.sw.add('dialog', DialogList(self.sw), '对话列表')
        
        # 切换
        self.sw.switch('sign').set_text("双击左边的项")

        self.st_dbname, self.st_file, self.st_page=None,None,None


    def start(self):
        self.main_window.mainloop()

    def flush(self):
        self.db.clear()
        self.db.construct_node()

    # 切换到某个文件
    def switch_file_dir(self, dir: str):
        self.sw.get('pdf').open_path(dir+'show.pdf')

    def open_subwindow(self):
        # 创建并显示子窗口
        if self.conv.winfo_exists() and not self.conv.winfo_viewable():
            self.conv.deiconify()

    def set_status(self, dbname: str|None, file: int|None, page: int|None):
        if dbname is not None: self.st_dbname = dbname
        if file is not None: self.st_file = file
        if page is not None: self.st_page = page

        state = (self.st_dbname, self.st_file, self.st_page)

        self.sw.get('sign').set_status(state)
        self.sw.get('html').set_status(state)
        self.sw.get('graph').set_status(state)
        self.sw.get('pdf').set_status(state)
        self.sw.get('graph0').set_status((self.st_dbname, -1, 0))

    def get_status(self):
        return (self.st_dbname, self.st_file, self.st_page)
    


def tests():
    # any2pdf(f"./workspace/db2/0",WORKDIR,'db2','0')
    # bCreateDatabase('db2')

    # root_dir = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    # file = os.path.normpath(os.path.join(root_dir, './pptx/politic.pptx'))
    # bAddFiles('signal', ['pdf/第05次课.pdf'])

    # generate_points('db',3)
    colors = [ 
        ['#E34234', '#FF0000', '#D1001C'],# red
        ['#FFA500', '#FF7F50', '#FF4500'],# orange
        ['#FFFF00', '#FFEA00', '#FFD700'],# yellow
        ['#00FF00', '#32CD32', '#008000'], # green
        ['#1E90FF', '#4169E1', '#0000FF'], # blue
        ['#9370DB', '#8A2BE2', '#800080'], # purple
        ['#FF69B4','#FFB6C1','#FFC0CB'], # pink
        ['#A0522D', '#8B4513', '#A52A2A'], # brown
        ['#D3D3D3', '#A9A9A9', '#808080'], # grey
        ['#00FFFF', '#00CED1', '#20B2AA'], # cyan
        ['#2E8B57', '#43CD80', '#54FF9F'], # sea green
        ['#FF4500', '#FF6347', '#FF7F50'], # coral
        ['#483D8B', '#6A5ACD', '#836FFF'], # slate blue
        ['#556B2F', '#6E8B3D', '#9ACD32'], # olive
        ['#8B7D6B', '#BC8F8F', '#CDB79E'], # rosy brown
        ['#00CED1', '#48D1CC', '#AFEEEE'], # turquoise
        ['#8B7E66', '#CDAF95', '#FFDAB9'], # peach puff
        ['#8A0707', '#CD5C5C', '#FF6A6A'], # dark red
        ['#FF8C00', '#FFA54F', '#FFD39B'], # dark orange
        ['#CDCD00', '#EEE685', '#FFFFE0'], # light yellow
        ['#006400', '#548B54', '#7FFF00'], # dark green
        ['#00008B', '#1C86EE', '#87CEFA'], # dark blue
        ['#551A8B', '#9A32CD', '#BF3EFF'], # dark purple
        ['#FF1493', '#EE82EE', '#FFB5C5'], # deep pink
        ['#8B4513', '#A0522D', '#CD853F'], # dark brown
        ['#2F4F4F', '#696969', '#A9A9A9'], # dark grey
        ['#008B8B', '#48D1CC', '#AFEEEE'], # dark cyan
        ['#FF6347', '#FF8247', '#FFA07A'], # tomato
        ['#4682B4', '#5CACEE', '#B0E2FF'], # steel blue
        ['#8B008B', '#9B30FF', '#E066FF'] # magenta
        ]
    db = 'signal'
    id = 4
    file_name = '第05次课.pdf'
    # subpoints_generator(db,id)
    # subpoints_extension(db,id)
    # fFlush()
    knowledge_density(db,id)
    # fFlush()
    generate_file_graph(db,id,colors)
    # fFlush()
    generate_points(db,id)
    # fFlush()
    html_generator(f"./workspace/{db}/{str(id)}/", f'mainpoints_{str(id)}.json', f"./{WORKDIR}/{db}/{str(id)}/")
    if file_name.endswith('.pdf'):
        shutil.copy2(f"./workspace/{db}/{str(id)}/{file_name}",f"./{WORKDIR}/{db}/{str(id)}/show.pdf")
    else :
        any2pdf(f"./workspace/{db}/{str(id)}",WORKDIR,db,str(id))
        id += 1
    fFlush()
    generate_main_graph(db,colors)
    pass

if not ONLY_FRONTEND:
    tests()
    pass


# print(bConversation('db', [(0,1,'你好','你好！'),(0,0,'这个PPT主要讲了什么？',None)]))

app = App()
fFlush()
app.start()