import json
import os
import pdfkit

def create_html_folder(directory_path):
    html_folder_path = os.path.join(directory_path, 'html')

    # 检查目录下是否存在名为 "html" 的文件夹
    if not os.path.exists(html_folder_path):
        try:
            # 创建 "html" 文件夹
            os.makedirs(html_folder_path)
            print(f'成功创建 "html" 文件夹：{html_folder_path}')
        except OSError as e:
            print(f'创建 "html" 文件夹时发生错误：{e}')
    else:
        print('目录下已存在 "html" 文件夹')

class EncyclopediaPageGenerator:
    def __init__(self, data):
        self.data = data
    def generate_link(self):
        # Process the list of links in searchresults
        relative_search_results_html = ""
        if self.data.get("searchresults", []) == []:
            relative_search_results_html = 'N/A'
        for link in self.data.get("searchresults", []):
            relative_search_results_html += f'<li><a href="{link["url"]}" target="_blank">{link["url"]}</a></li><br>'

        # Process the list of image paths
        images_html = ""
        if self.data.get("images", []) == []:
            images_html = 'N/A'
        for image_path in self.data.get("images", []):
            images_html += f'<img src="{image_path}" alt="Image" width="300">'

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.data["name"]}</title>
            <style>
                body {{
                    font-family: '微软雅黑', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(to right, #090740, #9d73c8);
                    color: #fff;
                    line-height: 1.6;
                }}
                h1, h2 {{
                    color: #fff;
                    border-bottom: 2px solid #8190c9;
                    padding-bottom: 5px;
                }}
                strong {{
                    color: #F9A825;
                }}
                p {{
                    margin-bottom: 15px;
                    color: #ddd;
                }}
                a {{
                    color: #27d2bb;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }}
                a:hover {{
                    text-decoration: underline;
                    color: #1a7d68;
                }}
                .container {{
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 30px;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                }}
                .info-box {{
                    border: 1px solid #72c8f3;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    background: #5414461a;
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                }}
                .img-box {{
                    border: 1px solid #08b4b4;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    background: rgba(2, 77, 94, 0.725);
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                }}
                .relative-search-results {{
                    max-width: 800px;
                    word-wrap: break-word;
                    list-style-type: none;
                    padding: 0;
                }}
                .relative-search-results li {{
                    margin-bottom: 5px;
                }}
                .images {{
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Relative Search Result:</h2>
                <ul class="relative-search-results">
                    {relative_search_results_html}
                </ul>
            </div>
        </body>
        </html>
        """

        return html
    def generate_html(self):
        # Process the list of links in searchresults
        relative_search_results_html = ""
        if self.data.get("searchresults", []) == []:
            relative_search_results_html = 'N/A'
        for link in self.data.get("searchresults", []):
            relative_search_results_html += f'<li><a href="{link["url"]}" target="_blank">{link["url"]}</a></li>'

        # Process the list of image paths
        images_html = ""
        if self.data.get("images", []) == []:
            images_html = 'N/A'
        for image_path in self.data.get("images", []):
            images_html += f'<img src="{image_path}" alt="Image" width="300">'

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.data["name"]}</title>
            <style>
                body {{
                    font-family: '微软雅黑', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(to right, #090740, #9d73c8);
                    color: #fff;
                    line-height: 1.6;
                }}
                h1, h2 {{
                    color: #fff;
                    border-bottom: 2px solid #8190c9;
                    padding-bottom: 5px;
                }}
                strong {{
                    color: #F9A825;
                }}
                p {{
                    margin-bottom: 15px;
                    color: #ddd;
                }}
                a {{
                    color: #27d2bb;
                    text-decoration: none;
                    transition: color 0.3s ease;
                }}
                a:hover {{
                    text-decoration: underline;
                    color: #1a7d68;
                }}
                .container {{
                    max-width: 800px;
                    margin: 40px auto;
                    padding: 30px;
                    background: rgba(0, 0, 0, 0.7);
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
                }}
                .info-box {{
                    border: 1px solid #72c8f3;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    background: #5414461a;
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                }}
                .img-box {{
                    border: 1px solid #08b4b4;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                    background: rgba(2, 77, 94, 0.725);
                    box-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
                }}
                .relative-search-results {{
                    max-width: 800px;
                    word-wrap: break-word;
                    list-style-type: none;
                    padding: 0;
                }}
                .relative-search-results li {{
                    margin-bottom: 5px;
                }}
                .images {{
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{self.data["name"]}</h1>
                <div class="info-box">
                    <h2>Definition</h2>
                    <p>{self.data["definition"]}</p>
                </div>
                <div class="info-box">
                    <h2>Information</h2>
                    <p>{self.data["information"]}</p>
                </div>
                <div class="info-box">
                    <h2>Usage</h2>
                    <p>{self.data["usage"]}</p>
                </div>

                <h2>Knowledge Density:</h2>
                <p>{self.data["knowledgeDensity"]:.4f}</p>
                <div class="img-box">
                    <h2>Relative Images</h2>
                    <p>                
                        <div class="images">
                            {images_html}
                        </div>
                    </p>
                </div>

            </div>
        </body>
        </html>
        """

        return html
    
def html_generator(file_path, file_name, save_path):
    # with open('..\\data\\workspace\\example_db\\0\\mainpoints_0.json', 'r', encoding='utf-8') as f:
    with open(file_path + file_name, 'r', encoding='utf-8') as f:
        datas = json.load(f)
        create_html_folder(save_path)
        main_points = datas['mainpoints']
        for main_pt in main_points:
            sub_points = main_pt['subpoints']
            for sub_pt in sub_points:
            # 生成HTML源码
                generator = EncyclopediaPageGenerator(sub_pt)
                html_source = generator.generate_html()
                link_source = generator.generate_link()
                # 将HTML源码保存到文件
                with open(f"{save_path}/html/{sub_pt['name']}.html", "w", encoding="utf-8") as file:
                    file.write(html_source)
                with open(f"{save_path}/html/{sub_pt['name']}_links.html", "w", encoding="utf-8") as file:
                    file.write(link_source)
                print(f"HTML file generation success.")
                print(f'PDF file generating...')
                config = pdfkit.configuration(wkhtmltopdf=r'./src/wkhtmltopdf/bin/wkhtmltopdf.exe')
                pdfkit.from_file(f"{save_path}/html/{sub_pt['name']}.html", f"{save_path}/html/{sub_pt['name']}.pdf", configuration=config)
                print(f"PDF file generation success, saved at {save_path}/html/{sub_pt['name']}.pdf.")
# test       
if __name__ == "__main__":   
    file_path = r'D:\\2023fall_HCI\\study-compass\\workspace\db2\\0\\'
    file_name = "mainpoints_0.json"
    save_path = r"D:\\2023fall_HCI\\study-compass\\workspace\db2\\0\\"
    html_generator(file_path, file_name, save_path)

# sample

# # 提供的字典数据
# data = {
#     "id": 0,
#     "pages": [1, 2],
#     "name": "美国基础教育的创新能力培养",
#     "definition": "美国基础教育注重培养学生的创新能力",
#     "information": "美国作为世界的创新高地，其基础教育体系培养出源源不断的创新活力，美国丰富的人才储备是其持续创新的基础。",
#     "usage": "通过基础教育体系培养学生的创新精神和实践能力，为社会培养能够推动科技和经济发展的人才。",
#     "images": [".\\image\\1-1.jpeg", ".\\image\\1-2.jpeg", ".\\image\\1-3.jpeg"],
#     "searchresults": ["www.4399.com", "www.example.com", "www.sample.com"],
#     "knowledgeDensity": 6.093338671601433
# }

# # 生成HTML源码
# generator = EncyclopediaPageGenerator(data)
# html_source = generator.generate_html()

# # 将HTML源码保存到文件
# with open("encyclopedia_page.html", "w", encoding="utf-8") as file:
#     file.write(html_source)

# print("HTML生成成功，保存在 encyclopedia_page.html 文件中。")
