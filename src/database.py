from hci_pipeline import *
import shutil


def fFlush(): pass


def bCreateDatabase(db: str) :
    base_dir = "./data"
    workspace_dir = "./workspace"
    db_work_dir = os.path.join(workspace_dir,db)
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
    db_dir = os.path.join(base_dir, db)
    os.makedirs(db_dir, exist_ok=True)
    os.makedirs(db_work_dir, exist_ok=True)
    print(f"Created database directory '{db_dir}' and ensured workspace directory '{workspace_dir}' exists.")


# Example usage of the function
def bAddFiles(db: str, paths: [str]) :
    base_dir = f"./workspace/{db}"
    show_dir = f"./data/{db}"
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
        fFlush()
        metadata_extractor(db,filepath,id)
        keyword_generator(db, id)
        fFlush()
        mainpoints_generator(db, id)
        fFlush()
        subpoints_generator(db,id)
        fFlush()
        subpoints_extension(db,id)
        fFlush()
        knowledge_density(db,id)
        fFlush()
        generate_file_graph(db,id,colors)
        fFlush()
        generate_points(db,id)
        fFlush()
        html_generator(f"./workspace/{db}/{str(id)}/", f'mainpoints_{str(id)}.json', f"./data/{db}/{str(id)}/")
        id += 1
    fFlush()
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
    weight = 0
    for mainpoint in main_points:
        weight += mainpoint["knowledgeDensity"]
    res["weight"] = weight
    res["sons"] = []
    num_each_file = int(10/len(main_points))+1
    for mainpoint in main_points:
        file_info = {}
        sub_color_index = 0
        file_info["name"] = mainpoint["keyword"]
        file_info["weight"] = mainpoint["knowledgeDensity"]
        file_info["file"] = mainpoint["id"]
        file_info["color"] = colors[color_index][sub_color_index]
        sub_color_index += 1
        sorted_mainpoints = sorted(mainpoint["mainpoints"], key=lambda x: x.get('knowledgeDensity', 0), reverse=True)
        new_mainpoints = []
        for i in sorted_mainpoints:
            new_mainpoints.append({"name":i["name"],"weight":i["knowledgeDensity"],"color":colors[color_index][sub_color_index],"file":mainpoint["id"],"page":i["pages"][0],"sons":[]})
        if len(new_mainpoints) >= num_each_file:
            file_info["sons"] = new_mainpoints[:num_each_file]
        else :
            file_info["sons"] = new_mainpoints
        res["sons"].append(file_info)
        color_index += 1

    save_path = f"./data/{db}/main_graph.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)   
        

                    
def generate_file_graph(db,id,colors):
    color_index = 0
    res = {}
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        main_points = json.load(file)
    res["name"] = main_points["keyword"]
    res["weight"] = main_points["knowledgeDensity"]
    res["file"] = main_points["id"]
    res["sons"] = []
    num_each_file = int(10/len(main_points["mainpoints"]))+1
    for mainpoint in main_points["mainpoints"]:
        sub_color_index = 0
        file_info = {}
        file_info["name"] = mainpoint["name"]
        file_info["weight"] = mainpoint["knowledgeDensity"]
        file_info["color"] = colors[color_index][sub_color_index]
        sub_color_index += 1
        file_info["file"] = main_points["id"]
        file_info["page"] = mainpoint["pages"][0]
        sorted_subpoints = sorted(mainpoint["subpoints"], key=lambda x: x.get('knowledgeDensity', 0), reverse=True)
        new_subpoints = []
        for i in sorted_subpoints:
            new_subpoints.append({"name":i["name"],"weight":i["knowledgeDensity"],"color":colors[color_index][sub_color_index],"file":main_points["id"],"page":i["pages"][0],"sons":[]})
        if len(new_subpoints) >= num_each_file:
            file_info["sons"] = new_subpoints[:num_each_file]
        else :
            file_info["sons"] = new_subpoints
        res["sons"].append(file_info)
        color_index += 1

    save_path = f"./data/{db}/{id}/file_graph.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)  

def generate_points(db,id):
    if not os.path.exists(f"./data/{db}/{str(id)}/html"):
        os.makedirs(f"./data/{db}/{str(id)}/html")
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
            new_mainpoint["subpoints"].append({"name":i["name"],"from_page":i["pages"][0],"to_page":i["pages"][1],"filename": f"./data/{db}/{str(id)}/html/{i['name']}.html"}) 
        res["mainpoints"].append(new_mainpoint)
    save_path = f"./data/{db}/{id}/points.json"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(res, file, ensure_ascii=False, indent=4)  

def bConversation(db: str, context) :
    question = ""
    background = ""
    log = ""
    page = ""
    for i in range(len(context)):
        if context[i][3] is not None:
            metadata_path = f"./workspace/{db}/{str(context[i][0])}/metadata_{str(context[i][0])}.json"
            with open(metadata_path, 'r', encoding='utf-8') as file:
                metadata = json.load(file)
            content = json.dumps(metadata, indent=4)
            content += f"\nHere is a question of the user:{context[i][2]}"
            content += f"\nThe question is based on the context above.It is about the content in page {context[i][1]} "
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
    prompt += f"\n The content above is the background information of the question.The question ia mainly based on the content in page {page}. So you need to pay more attention.\n"
    prompt += question
    prompt += "\nPlease based on your previous answers and background information,answer the question above.Your answer should  be in Chinese."
    res = query_gpt4(prompt)
    return res   

if __name__ == "__main__":
    bCreateDatabase("example_db")
    example_paths = ["D:/大三上/人机交互/study-compass/pdf/safety.pdf"]
    bAddFiles("example_db", example_paths)
    # knowledge_density("example_db",0)
    # knowledge_density("example_db",0)
    # context = [(0, 1, "What is the background of the question?","背景信息显示，这个问题涉及对美国基础教育的一系列误解和批评，以及对这些误解的分析和反驳。作者通过具体数据和实例，揭示了美国基础教育的实际效果和成就，并进一步探讨了美国基础教育的优势，分析了保持高质量的原因，并讨论了美国的基础教育对中国教育体系的可能启示。文章探求的是美国基础教育是否真的如一些批评所言不堪，以及在肯定其成就的同时，中国教育改革可以从中学到什么教训，以发展出更适合中国国情的教育体系。"),(0, 2, "中美基础教育哪个好?",None)]
    # bConversation("example_db",context)
    # colors = [ 
    #     ['#E34234', '#FF0000', '#D1001C'],# red
    #     ['#FFA500', '#FF7F50', '#FF4500'],# orange
    #     ['#FFFF00', '#FFEA00', '#FFD700'],# yellow
    #     ['#00FF00', '#32CD32', '#008000'], # green
    #     ['#1E90FF', '#4169E1', '#0000FF'], # blue
    #     ['#9370DB', '#8A2BE2', '#800080'], # purple
    #     ['#FF69B4','#FFB6C1','#FFC0CB'], # pink
    #     ['#A0522D', '#8B4513', '#A52A2A'], # brown
    #     ['#D3D3D3', '#A9A9A9', '#808080'], # grey
    #     ['#00FFFF', '#00CED1', '#20B2AA'], # cyan
    #     ['#2E8B57', '#43CD80', '#54FF9F'], # sea green
    #     ['#FF4500', '#FF6347', '#FF7F50'], # coral
    #     ['#483D8B', '#6A5ACD', '#836FFF'], # slate blue
    #     ['#556B2F', '#6E8B3D', '#9ACD32'], # olive
    #     ['#8B7D6B', '#BC8F8F', '#CDB79E'], # rosy brown
    #     ['#00CED1', '#48D1CC', '#AFEEEE'], # turquoise
    #     ['#8B7E66', '#CDAF95', '#FFDAB9'], # peach puff
    #     ['#8A0707', '#CD5C5C', '#FF6A6A'], # dark red
    #     ['#FF8C00', '#FFA54F', '#FFD39B'], # dark orange
    #     ['#CDCD00', '#EEE685', '#FFFFE0'], # light yellow
    #     ['#006400', '#548B54', '#7FFF00'], # dark green
    #     ['#00008B', '#1C86EE', '#87CEFA'], # dark blue
    #     ['#551A8B', '#9A32CD', '#BF3EFF'], # dark purple
    #     ['#FF1493', '#EE82EE', '#FFB5C5'], # deep pink
    #     ['#8B4513', '#A0522D', '#CD853F'], # dark brown
    #     ['#2F4F4F', '#696969', '#A9A9A9'], # dark grey
    #     ['#008B8B', '#48D1CC', '#AFEEEE'], # dark cyan
    #     ['#FF6347', '#FF8247', '#FFA07A'], # tomato
    #     ['#4682B4', '#5CACEE', '#B0E2FF'], # steel blue
    #     ['#8B008B', '#9B30FF', '#E066FF'] # magenta
    #     ]
    # generate_main_graph("example_db",colors)
    # generate_file_graph("example_db",1,colors)
    # generate_points("example_db",1)