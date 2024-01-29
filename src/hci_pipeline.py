from utils import *
from guideline import *
from mainpoints import *
import json
import glob
import numpy as np
import math
from html_generator import *
from scipy.stats import norm

os.environ["OPENAI_API_KEY"] = "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"


def save_curtail_subpoints_to_file_as_json(subpoints, file_name):
    # Create a directory for storing the metadata files if it doesn't exist
    directory = "curtail_subpoints_files"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the path for the metadata file
    subpoints_file_path = os.path.join(directory, f"curtail_subpoints_{file_name}.json")

    # Write the metadata to the file as JSON
    with open(subpoints_file_path, 'w', encoding='utf-8') as file:
        json.dump(subpoints, file, ensure_ascii=False, indent=4)

    return subpoints_file_path


def save_metadata_to_file_as_json(metadata, id,db):
    # Create a directory for storing the metadata files if it doesn't exist
    directory = f"./workspace/{db}/{str(id)}"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the path for the metadata file
    metadata_file_path = os.path.join(directory, f"metadata_{str(id)}.json")

    # Write the metadata to the file as JSON
    with open(metadata_file_path, 'w', encoding='utf-8') as file:
        json.dump(metadata, file, ensure_ascii=False, indent=4)

    return metadata_file_path


def save_curtail_mainpoints_to_file_as_json(mainpoints):
    # Create a directory for storing the metadata files if it doesn't exist
    directory = "curtail_mainpoints_files"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Define the path for the metadata file
    mainpoints_file_path = os.path.join(directory, f"curtail_mainpoints.json")

    # Write the metadata to the file as JSON
    with open(mainpoints_file_path, 'w', encoding='utf-8') as file:
        json.dump(mainpoints, file, ensure_ascii=False, indent=4)

    return mainpoints_file_path

def metadata_extractor(db,file_path,id):
    file_name = file_path.split('/')[-1]
    if os.path.isfile(file_path):
        if file_name.endswith('.pptx'):
            metadata = extract_metadata_from_pptx_langchain(file_path)
            extract_images_from_pptx(file_path,f"./workspace/{db}/{str(id)}/images")
        elif file_path.endswith('.docx'):
            metadata = extract_text_from_docx(file_path)
            extract_images_from_docx(file_path,f"./workspace/{db}/{str(id)}/images")
        elif file_path.endswith('.pdf'):
            metadata = extract_text_with_page_numbers_pdf(file_path)
            extract_images_from_pdf(file_path,f"./workspace/{db}/{str(id)}/images")
    save_metadata_to_file_as_json(metadata,id,db)
    
    
def keyword_generator(db,id):
    metadata_path = os.path.join(f"./workspace/{db}/{str(id)}", f"metadata_{str(id)}.json")
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    key_word_gen(metadata,f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json")
    


def mainpoints_generator(db,id):
    metadata_path = f"./workspace/{db}/{str(id)}/metadata_{str(id)}.json"
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    mainknowledge_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainknowledge_path, 'r', encoding='utf-8') as file:
        main_knowledge = json.load(file)
    main_know = main_knowledge
    main_know["mainpoints"] = knowledge_points_gen(metadata)
    with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
        json.dump(main_know, file, ensure_ascii=False, indent=4)   
    

def subpoints_generator(db,id):
    metadata_path = f"./workspace/{db}/{str(id)}/metadata_{str(id)}.json"
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        mainpoints = json.load(file)
    for i in mainpoints["mainpoints"]:
        if "subpoints" in i:
            continue 
        child = subpoints_gen(i,metadata)
        child = add_image(child,db,id)
        i["subpoints"] = child
        with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
            json.dump(mainpoints, file, ensure_ascii=False, indent=4) 


def subpoints_extension(db,id):
    mainpoints_path =f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        mainpoints = json.load(file)
    for i in mainpoints["mainpoints"]:
        child = information_extension(i["subpoints"],i)
        i["subpoints"] = child
        with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
            json.dump(mainpoints, file, ensure_ascii=False, indent=4) 


def subpoints_learningplan(db,id):
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        mainpoints = json.load(file)
    for index, item in enumerate(mainpoints["learningplan"]):
        for i in mainpoints["mainpoints"]:
            if i['name'] == item :
                i["guideline"] = sub_sequence_gen(i["subpoints"],index)
                with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
                    json.dump(mainpoints, file, ensure_ascii=False, indent=4) 



def main_points_curtail():
    # 读取JSON文件
    mainpoints = []
    for file_path in glob.glob(os.path.join("mainpoints_files", '*.json')):
        second_underscore_index = file_path.find('_', file_path.find('_') + 1)
        last_dot_index = file_path.rfind('.')
        extracted_text = file_path[second_underscore_index + 1:last_dot_index]
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            temp = [{"id": point["id"],"filename":extracted_text, "name": point["name"], "pages": point["pages"]} for point in data["mainpoints"]]
            mainpoints.append(temp)
    content = json.dumps(mainpoints, indent=4)
    res = "No brackets found or incomplete pair"
    while( res == "No brackets found or incomplete pair"):
        question  =f"The content above give you some mainpoints about a certain field.Please based on the content above and your knowledge,select at most 10 most important mainpoints ."
        appendix = " Your answer must be in the form of a list of json.. Do not include annotation or anything else! Here is the example:[{id: xx,filename:xx,pages:(xx,xx), name : xx},...] 'id' is the index of the mainpoints, filename is the file this main points belong to. 'pages' is  a tuple that contains the begin number and end number of the pages that belongs to the main point,'name' is the general description of the main point.Your answer must be in Chinese."
        prompt = content + question + appendix
        res = query_gpt4(prompt)
        res = extract_including_brackets(res)
        # print(res)
        
        print("Main points successfully curtailed.")
    data_list = ast.literal_eval(res)
    save_curtail_mainpoints_to_file_as_json(data_list)
    return data_list


def sub_points_curtail(file_path):
    subpoints = []
    file_name = file_path.split('/')[-1]
    mainpoints_path = os.path.join("mainpoints_files", f"mainpoints_{file_name}.json")
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        mainpoints = json.load(file)
        for mainpoint in mainpoints["mainpoints"]:
            for subpoint in mainpoint["subpoints"]:
                # 移除不需要的项
                subpoint.pop("images", None)
                subpoint.pop("searchresults", None)
                # 添加mainpoint项
                subpoint["mainpoint"] = mainpoint["name"]
                subpoints.append(subpoint)
    content = json.dumps(mainpoints, indent=4)
    res = "No brackets found or incomplete pair"
    while( res == "No brackets found or incomplete pair"):
        question  =f"The content above give you some subpoints about a certain field.Please based on the content above and your knowledge,select at most 10 most important subpoints ."
        appendix = " Your answer must be in the form of a list of json.. Do not include annotation or anything else! Here is the example:[{id: xx,mainpoint:xx,pages:(xx,xx), name : xx},...] 'id' is the index of the subpoints, mainpoint is the main point this sub point belong to. 'pages' is  a tuple that contains the begin number and end number of the pages that belongs to the sub point,'name' is the general description of the main point.Your answer must be in Chinese."
        prompt = content + question + appendix
        res = query_gpt4(prompt)
        res = extract_including_brackets(res)
        # print(res)
            
    print("Sub points successfully curtailed.")
    data_list = ast.literal_eval(res)
    save_curtail_subpoints_to_file_as_json(data_list,file_name)
    return data_list


def calculate_euclidean_similarity(text):
    if not text:
        return 0
    char_freq = {}
    for char in text:
        if char in char_freq:
            char_freq[char] += 1
        else:
            char_freq[char] = 1
    freq_vector = np.array(list(char_freq.values())) / len(text)
    ideal_vector = np.ones(len(char_freq)) / len(freq_vector)
    euclidean_distance = np.linalg.norm(freq_vector - ideal_vector)
    similarity = 1 / (1 + euclidean_distance)

    return similarity


def knowledge_density(db,id):
    metadata_path = f"./workspace/{db}/{str(id)}/metadata_{str(id)}.json"
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    mainpoints_path = f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json"
    with open(mainpoints_path, 'r', encoding='utf-8') as file:
        mainpoints = json.load(file)
    main_density = 0.0
    for mainpoint in mainpoints["mainpoints"]:
        for subpoint in mainpoint["subpoints"]:
            if "knowledgeDensity" in subpoint:
                continue
            tot_page = int(mainpoints["mainpoints"][-1]['pages'][1])
            density = 0.0
            begin = subpoint["pages"][0]
            end = subpoint["pages"][1]
            density += 2.5*(end-begin+1)/tot_page
            tot_words = len(json.dumps(metadata, indent=4))
            context = []
            for index in range(begin-1,end):
                print(index)
                context.append(metadata[index])
            context = json.dumps(context, indent=4)
            words_num = len(context)
            density += 4 * words_num/tot_words
            density += calculate_euclidean_similarity(context)
            content = f"The given content is some information about {mainpoint['name']}.Please base on your knowledge about this field,give a intger from 1 to 5 to evaluate the knowledge density of the given content.The bigger the number is,the more knowledge the content above contains.Your answer should only be an integer!Do not include anything else!"
            prompt = context + content
            while True:
                try:
                    res = query_gpt4(prompt)
                    density += 0.5*int(res)
                    break
                except (SyntaxError, ValueError):
            # 如果解析失败，打印错误信息并继续循环
                    print("Error in parsing the response. Trying again...")
            subpoint["knowledgeDensity"]= density 
            with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
                json.dump(mainpoints, file, ensure_ascii=False, indent=4)  
            print("Knowledge density succussfully generated!")
    subpoints_list = []
    for i in mainpoints["mainpoints"]:
        subpoints_list.extend(i["subpoints"])
    subpoints_list.sort(key=lambda x: x["knowledgeDensity"], reverse=False)
    n = len(subpoints_list)
    num_middle = int(np.ceil(2 * n / 3))  
    num_sides = n - num_middle 
    num_left = num_sides // 2  
    num_right = n - num_left - num_middle  
    samples_left = np.linspace(0.1, 1/3, num_left, endpoint=False)
    samples_middle = np.linspace(1/3, 2/3, num_middle, endpoint=False)
    samples_right = np.linspace(2/3, 1, num_right, endpoint=True)
    sample = np.sort(np.concatenate((samples_left, samples_middle, samples_right)))
    for j, new_value in zip(subpoints_list, sample):
        j["weight"] = new_value   
    for mainpoint in mainpoints["mainpoints"]:
        for subpoint in mainpoint["subpoints"]:
            main_density += subpoint["knowledgeDensity"]
        mainpoint["knowledgeDensity"] = main_density
    total_density = 0.0
    for mainpoint in mainpoints["mainpoints"]:
        total_density += mainpoint["knowledgeDensity"]
    mainpoints["knowledgeDensity"] = total_density
    with open(f"./workspace/{db}/{str(id)}/mainpoints_{str(id)}.json", 'w', encoding='utf-8') as file:
        json.dump(mainpoints, file, ensure_ascii=False, indent=4)  



def answer(log,file_path,page:Tuple,question):
    context = []
    file_name = file_path.split('/')[-1]
    metadata_path = os.path.join("metadata_files", f"metadata_{file_name}.json")
    with open(metadata_path, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    for i in range(page[0]-1,page[1]):
        context.append(metadata[i])
    context = json.dumps(context, indent=4)
    prompt = ""
    prompt += log
    prompt += "\n The content above is the log of the user's questions.(You can ignore if it is blank).\n"
    prompt += context
    prompt += "\nThe content ablove is some background information of the user's questions\n"
    prompt += question
    prompt += "\nPlease based on your previous answers and background information,answer the question above.Your answer should  be in Chinese."
    res = query_gpt4(prompt)
    return res   
        
if __name__ == "__main__":
    # metadata_extractor("../word/课程论文.docx")
    # print(keyword_generator("../word/课程论文.docx"))
    # print(mainpoints_generator("../word/课程论文.docx"))
    # print(subpoints_generator("../word/课程论文.docx"))
    # print(subpoints_extension("../word/课程论文.docx"))
    # print(subpoints_learningplan("../word/课程论文.docx"))
    # main_points_curtail()
    # sub_points_curtail("../word/课程论文.docx")
    # knowledge_density("../word/课程论文.docx")
    print(answer("","../word/课程论文.docx",(1,2),"美国和中国哪个的基础教育比较好？"))
    
    
    
    # metadata = extract_text_with_page_numbers_pdf("../pdf/safety.pdf")
    # extract_images_from_pdf("../pdf/safety.pdf","image")
    # main_knowledge = knowledge_points_gen(metadata)
    # print(main_knowledge)
    
    # metadata = extract_text_from_docx("../word/课程论文.docx")
    # extract_images_from_docx("../word/课程论文.docx","image")
    # key_word = key_word_gen(metadata)
    # print(key_word)
    # main_knowledge = knowledge_points_gen(metadata)
                
                
    # extract_images_from_pptx("../pptx/compile.pptx", "./extracted_images")
    # metadata = extract_metadata_from_pptx("../pptx/Testing.pptx")
    # main_knowledge = knowledge_points_gen(metadata)
    
    # metadata = extract_metadata_from_pptx_langchain("../pptx/compile.pptx")
#     main_knowledge = knowledge_points_gen(metadata)
#     main_knowledge = main_sequence_gen(main_knowledge)
#     print(main_knowledge)
#     for i in main_knowledge["mainpoints"]:
#         child = subpoints_gen(i,metadata)
#         child = add_image(child)
#         child = information_extension(child,i)
#         i["subpoints"] = child
#     for index, item in enumerate(main_knowledge["learningplan"]):
#         for i in main_knowledge["mainpoints"]:
#             if i['name'] == item :
#                 i["guideline"] = sub_sequence_gen(i["subpoints"],index)
    
#     print(main_knowledge)
    
# with open('compile.json', 'w', encoding='utf-8') as json_file:
#     json.dump(main_knowledge, json_file, ensure_ascii=False, indent=4)

    



# "Please give me the main points of the content.the given main points must summarize the whole content.So do not begin summarize until you have read all the contents.\
#             You should think carefully and remember that the number of the  main knowledge points should be less than 10.You can leave out some less important points.\
#             Your answer must be in the form of a list of json.Here is the example:  [{id: xx,name : xx,pages : (xx, xx) },...]\
#             'id' in the order of 0、1、2,name is the content of the main point,and does not need to be the same as the content of any title.pages is  a tuple that contains the begin page number  and end page number of the main point.\
#             All tuples connected end-to-end should cover all page numbers"
