import os
import win32com.client
import gc

# Word
def word2Pdf(savePath,filePath, words):
    # If there are no files, print a message and exit
    if len(words) < 1:
        print("\n【No Word files】\n")
        return
    
    # Start the conversion
    print("\n【Starting Word to PDF conversion】")
    try:
        print("Opening Word process...")
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = 0
        word.DisplayAlerts = False
        doc = None

        for i in range(len(words)):
            print(i)
            fileName = words[i]  # File name
            fromFile = filePath + '/' +fileName  # File path
            toFileName = 'show.pdf'  # Generated file name
            toFile = savePath + '/' + toFileName  # Generated file path

            print("Converting: " + fileName + " file...")
            # Handle errors for individual files without affecting others
            try:
                doc = word.Documents.Open(fromFile)
                doc.SaveAs(toFile, 17)  # All generated PDFs will be in the PDF folder
                print("Conversion to: " + toFileName + " completed")
            except Exception as e:
                print(e)

        # Close Word process
        print("All Word files have been printed")
        print("Closing Word process...\n")
        doc.Close()
        doc = None
        word.Quit()
        word = None
    except Exception as e:
        print(e)
    finally:
        gc.collect()

# Excel
def excel2Pdf(filePath, excels):
    # If there are no files, print a message and exit
    if len(excels) < 1:
        print("\n【No Excel files】\n")
        return
    
    # Start the conversion
    print("\n【Starting Excel to PDF conversion】")
    try:
        print("Opening Excel process...")
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = 0
        excel.DisplayAlerts = False
        wb = None
        ws = None

        for i in range(len(excels)):
            print(i)
            fileName = excels[i]  # File name
            fromFile = os.path.join(filePath, fileName)  # File path

            print("Converting: " + fileName + " file...")
            # Handle errors for individual files without affecting others
            try:
                wb = excel.Workbooks.Open(fromFile)
                for j in range(wb.Worksheets.Count):  # Number of worksheets, a workbook may have multiple sheets
                    toFileName = addWorksheetsOrder(fileName, j + 1)  # Generated file name
                    toFile = toFileJoin(filePath, toFileName)  # Generated file path

                    ws = wb.Worksheets(j + 1)
                    ws.ExportAsFixedFormat(0, toFile)  # Print each sheet
                    print("Conversion to: " + toFileName + " file completed")
            except Exception as e:
                print(e)

        # Close Excel process
        print("All Excel files have been printed")
        print("Closing Excel process...\n")
        ws = None
        wb.Close()
        wb = None
        excel.Quit()
        excel = None
    except Exception as e:
        print(e)
    finally:
        gc.collect()

# PPT
def ppt2Pdf(savePath,filePath, ppts):
    # If there are no files, print a message and exit
    if len(ppts) < 1:
        print("\n【No PPT files】\n")
        return
    
    # Start the conversion
    print("\n【Starting PPT to PDF conversion】")
    # try:
    print("Opening PowerPoint process...")
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    ppt = None
    # Handle errors for individual files without affecting others

    for i in range(len(ppts)):
        fileName = ppts[i]  # File name
        fromFile = filePath + '/' +fileName  # File path
        toFileName = 'show.pdf' # Generated file name
        toFile = savePath + '/' + toFileName  # Generated file path

        print("Converting: " + fileName + " file...")
        # try:
        ppt = powerpoint.Presentations.Open(fromFile, WithWindow=False)
        if ppt.Slides.Count > 0:
            ppt.SaveAs(toFile, 32)  # If it's empty, a prompt will appear (no solution yet)
            print("Conversion to: " + toFileName + " file completed")
        else:
            print("(Error, unexpected: This file is empty, skipping this file)")
        # except Exception as e:
        #     print(e)

    # Close PowerPoint process
    print("All PPT files have been printed")
    print("Closing PowerPoint process...\n")
    ppt.Close()
    ppt = None
    powerpoint.Quit()
    powerpoint = None
    # except Exception as e:
    #     print(e)
    # finally:
    #     gc.collect()

# Change file extension
def changeSufix2Pdf(file):
    return file[:file.rfind('.')] + ".pdf"

# Add worksheet order
def addWorksheetsOrder(file, i):
    return file[:file.rfind('.')] + "_Worksheet" + str(i) + ".pdf"

# Conversion address
def toFileJoin(filePath, file):
    return os.path.join(filePath, 'pdf', file[:file.rfind('.')] + ".pdf")

def any2pdf(filePath,savePath,db,id):
    # Start the program
    print("====================Program Start====================")
    print(
        "【Program Function】Generate a PDF file for each ppt, excel, and word in the target path, and store them in the newly generated pdf folder (Office must be installed, excluding subfolders)")
    print(
        "Note: If a PPT and Excel file are empty, an error will occur and skip this file. If the conversion time for PPT is too long, check if there is a pop-up window waiting for confirmation. Currently unable to completely solve the window problem of PPT (empty error has been resolved). The time may be relatively long when closing the process, about ten seconds, please be patient.")
    
    # Target file path
    # filePath = input("Enter the target path: (If it is the current path: " + os.getcwd() + ", please press Enter)\n")
    # filePath = r"D:\2023fall_HCI\study-compass\pptx"
    # Target path, if no path is entered, it is the current path
    if filePath == "":
        filePath = os.getcwd()
    
    # Classify all files in the target folder, open only one process when converting
    words = []
    ppts = []
    
    for fn in os.listdir(filePath):
        if fn.endswith(('.doc', 'docx')):
            words.append(fn)
        if fn.endswith(('.ppt', 'pptx')):
            ppts.append(fn)
    
    # Call methods
    print("====================Start Conversion====================")
    
    # Save path: create a new pdf folder, all generated PDF files are placed in it
    savefolder = savePath + db + '/' + id
    word2Pdf(savefolder, filePath,words)
    ppt2Pdf(savefolder, filePath,ppts)
    print("====================Conversion End====================")
    print("\n====================Program End====================")

# import os, win32com.client, gc
 
# # Word
# def word2Pdf(filePath, words):
#     # 如果没有文件则提示后直接退出
#     if (len(words) < 1):
#         print("\n【无 Word 文件】\n")
#         return
#     # 开始转换
#     print("\n【开始 Word -> PDF 转换】")
#     try:
#         print("打开 Word 进程...")
#         word = win32com.client.Dispatch("Word.Application")
#         word.Visible = 0
#         word.DisplayAlerts = False
#         doc = None
#         for i in range(len(words)):
#             print(i)
#             fileName = words[i]  # 文件名称
#             fromFile = os.path.join(filePath, fileName)  # 文件地址
#             toFileName = changeSufix2Pdf(fileName)  # 生成的文件名称
#             toFile = toFileJoin(filePath, toFileName)  # 生成的文件地址
 
#             print("转换：" + fileName + "文件中...")
#             # 某文件出错不影响其他文件打印
#             try:
#                 doc = word.Documents.Open(fromFile)
#                 doc.SaveAs(toFile, 17)  # 生成的所有 PDF 都会在 PDF 文件夹中
#                 print("转换到：" + toFileName + "完成")
#             except Exception as e:
#                 print(e)
#             # 关闭 Word 进程
#         print("所有 Word 文件已打印完毕")
#         print("结束 Word 进程...\n")
#         doc.Close()
#         doc = None
#         word.Quit()
#         word = None
#     except Exception as e:
#         print(e)
#     finally:
#         gc.collect()
 
 
# # Excel
# def excel2Pdf(filePath, excels):
#     # 如果没有文件则提示后直接退出
#     if (len(excels) < 1):
#         print("\n【无 Excel 文件】\n")
#         return
#     # 开始转换
#     print("\n【开始 Excel -> PDF 转换】")
#     try:
#         print("打开 Excel 进程中...")
#         excel = win32com.client.Dispatch("Excel.Application")
#         excel.Visible = 0
#         excel.DisplayAlerts = False
#         wb = None
#         ws = None
#         for i in range(len(excels)):
#             print(i)
#             fileName = excels[i]  # 文件名称
#             fromFile = os.path.join(filePath, fileName)  # 文件地址
 
#             print("转换：" + fileName + "文件中...")
#             # 某文件出错不影响其他文件打印
#             try:
#                 wb = excel.Workbooks.Open(fromFile)
#                 for j in range(wb.Worksheets.Count):  # 工作表数量，一个工作簿可能有多张工作表
#                     toFileName = addWorksheetsOrder(fileName, j + 1)  # 生成的文件名称
#                     toFile = toFileJoin(filePath, toFileName)  # 生成的文件地址
 
#                     ws = wb.Worksheets(j + 1)  # 若为[0]则打包后会提示越界
#                     ws.ExportAsFixedFormat(0, toFile)  # 每一张都需要打印
#                     print("转换至：" + toFileName + "文件完成")
#             except Exception as e:
#                 print(e)
#         # 关闭 Excel 进程
#         print("所有 Excel 文件已打印完毕")
#         print("结束 Excel 进程中...\n")
#         ws = None
#         wb.Close()
#         wb = None
#         excel.Quit()
#         excel = None
#     except Exception as e:
#         print(e)
#     finally:
#         gc.collect()
 
 
# # PPT
# def ppt2Pdf(filePath, ppts):
#     # 如果没有文件则提示后直接退出
#     if (len(ppts) < 1):
#         print("\n【无 PPT 文件】\n")
#         return
#     # 开始转换
#     print("\n【开始 PPT -> PDF 转换】")
#     # try:
#     print("打开 PowerPoint 进程中...")
#     powerpoint = win32com.client.Dispatch("PowerPoint.Application")
#     ppt = None
#     # 某文件出错不影响其他文件打印

#     for i in range(len(ppts)):
#         print(i)
#         fileName = ppts[i]  # 文件名称
#         fromFile = os.path.join(filePath, fileName)  # 文件地址
#         toFileName = changeSufix2Pdf(fileName)  # 生成的文件名称
#         toFile = toFileJoin(filePath, toFileName)  # 生成的文件地址

#         print("转换：" + fileName + "文件中...")
#         # try:
#         ppt = powerpoint.Presentations.Open(fromFile, WithWindow=False)
#         if ppt.Slides.Count > 0:
#             ppt.SaveAs(toFile, 32)  # 如果为空则会跳出提示框（暂时没有找到消除办法）
#             print("转换至：" + toFileName + "文件完成")
#         else:
#             print("（错误，发生意外：此文件为空，跳过此文件）")
#         # except Exception as e:
#         #     print(e)
#     # 关闭 PPT 进程
#     print("所有 PPT 文件已打印完毕")
#     print("结束 PowerPoint 进程中...\n")
#     ppt.Close()
#     ppt = None
#     powerpoint.Quit()
#     powerpoint = None
#     # except Exception as e:
#     #     print(e)
#     # finally:
#     #     gc.collect()
 
 
# # 修改后缀名
# def changeSufix2Pdf(file):
#     return file[:file.rfind('.')] + ".pdf"
 
 
# # 添加工作簿序号
# def addWorksheetsOrder(file, i):
#     return file[:file.rfind('.')] + "_工作表" + str(i) + ".pdf"
 
 
# # 转换地址
# def toFileJoin(filePath, file):
#     return os.path.join(filePath, 'pdf', file[:file.rfind('.')] + ".pdf")
 

# def any2pdf(filePath):
#     # 开始程序
#     print("====================程序开始====================")
#     print(
#         "【程序功能】将目标路径下内所有的 ppt、excel、word 均生成一份对应的 PDF 文件，存在新生成的 pdf 文件夹中（需已经安装office，不包括子文件夹）")
#     print(
#         "注意：若某 PPT 和 Excel 文件为空，则会出错跳过此文件。若转换 PPT 时间过长，请查看是否有报错窗口等待确认，暂时无法彻底解决 PPT 的窗口问题（为空错误已解决）。在关闭进程过程中，时间可能会较长，十秒左右，请耐心等待。")
    
    
#     # 需要转换的文件路径
#     # filePath = input("输入目标路径：(若为当前路径：" + os.getcwd() + "，请直接回车）\n")
#     # filePath = r"D:\2023fall_HCI\study-compass\pptx"
#     # 目标路径，若没有输入路径则为当前路径
#     if (filePath == ""):
#         filePath = os.getcwd()
    
#     # 将目标文件夹所有文件归类，转换时只打开一个进程
#     words = []
#     ppts = []
#     excels = []
    
#     for fn in os.listdir(filePath):
#         if fn.endswith(('.doc', 'docx')):
#             words.append(fn)
#         if fn.endswith(('.ppt', 'pptx')):
#             ppts.append(fn)
#         if fn.endswith(('.xls', 'xlsx')):
#             excels.append(fn)
    
#     # 调用方法
#     print("====================开始转换====================")
    
#     # 保存路径：新建 pdf 文件夹，所有生成的 PDF 文件都放在里面
#     folder = filePath + '\\pdf\\'
#     if not os.path.exists(folder):
#         os.makedirs(folder)
    
#     word2Pdf(filePath, words)
#     excel2Pdf(filePath, excels)
#     ppt2Pdf(filePath, ppts)
#     print("====================转换结束====================")
#     print("\n====================程序结束====================")

# test

# os.system("pause")

# import os
# from docx2pdf import convert
# from pptx import Presentation

# def convert_docx_to_pdf(input_folder, output_folder):
#     # 获取输入文件夹中的所有.docx文件
#     docx_files = [f for f in os.listdir(input_folder) if f.endswith(".docx")]

#     # 转换每个.docx文件为.pdf
#     for docx_file in docx_files:
#         docx_path = os.path.join(input_folder, docx_file)
#         pdf_path = os.path.join(output_folder, "pdf", f"{os.path.splitext(docx_file)[0]}.pdf")
#         convert(docx_path, pdf_path)

# def convert_ppt_to_pdf(input_folder, output_folder):
#     # 获取输入文件夹中的所有.ppt和.pptx文件
#     ppt_files = [f for f in os.listdir(input_folder) if f.endswith(".ppt") or f.endswith(".pptx")]

#     # 转换每个.ppt和.pptx文件为.pdf
#     for ppt_file in ppt_files:
#         ppt_path = os.path.join(input_folder, ppt_file)
#         pdf_path = os.path.join(output_folder, "pdf", f"{os.path.splitext(ppt_file)[0]}.pdf")

#         # 使用python-pptx库打开PPT文件
#         presentation = Presentation(ppt_path)

#         # 创建一个PDF文档
#         pdf_writer = Presentation()
#         pdf_writer.save(pdf_path)

#         # 将每个幻灯片另存为PDF
#         for i, slide in enumerate(presentation.slides):
#             image_path = os.path.join(output_folder, "pdf", f"temp_{i}.png")
#             slide.export(image_path, "PNG")
#             pdf_writer.slides.add_slide().shapes.add_picture(image_path, 0, 0, width=None, height=None)
#             os.remove(image_path)

#         # 保存PDF文档
#         pdf_writer.save(pdf_path)

# # 输入文件夹路径
# input_folder_path = r"D:\2023fall_HCI\study-compass\pptx"

# # 输出文件夹路径
# output_folder_path = r"D:\2023fall_HCI\study-compass\pptx"

# # 创建 pdf 子文件夹
# pdf_folder_path = os.path.join(output_folder_path, 'pdf')
# if not os.path.exists(pdf_folder_path):
#     os.makedirs(pdf_folder_path)

# # 调用函数进行转换
# convert_docx_to_pdf(input_folder_path, output_folder_path)
# convert_ppt_to_pdf(input_folder_path, output_folder_path)
# import os
# from docx2pdf import convert
# from pptx import Presentation
# from pptx.util import Inches, Pt
# from PIL import Image

# def convert_docx_to_pdf(input_folder, output_folder):
#     docx_files = [f for f in os.listdir(input_folder) if f.endswith(".docx")]

#     for docx_file in docx_files:
#         docx_path = os.path.join(input_folder, docx_file)
#         pdf_path = os.path.join(output_folder, "pdf", f"{os.path.splitext(docx_file)[0]}.pdf")
#         convert(docx_path, pdf_path)

# def convert_ppt_to_pdf(input_folder, output_folder):
#     ppt_files = [f for f in os.listdir(input_folder) if f.endswith(".ppt") or f.endswith(".pptx")]

#     for ppt_file in ppt_files:
#         ppt_path = os.path.join(input_folder, ppt_file)
#         pdf_path = os.path.join(output_folder, "pdf", f"{os.path.splitext(ppt_file)[0]}.pdf")

#         presentation = Presentation(ppt_path)
#         pdf_writer = Presentation()

#         for i, slide in enumerate(presentation.slides):
#             image_path = os.path.join(output_folder, "pdf", f"temp_{i}.png")

#             # 检查幻灯片布局中是否有占位符
#             if len(slide.slide_layout.placeholders) > 0:
#                 # 将幻灯片保存为图像
#                 image_part = slide.slide_layout.placeholders[0].image
#                 image_part.save(image_path)

#                 # 插入图像到 PDF 中
#                 pdf_slide = pdf_writer.slides.add_slide(pdf_writer.slide_layouts[5])  # 使用空白幻灯片布局
#                 pdf_img = Image.open(image_path)
#                 pdf_img_width, pdf_img_height = pdf_img.size
#                 pdf_slide.shapes.add_picture(image_path, Inches(0), Inches(0), width=Inches(pdf_img_width / Pt(72)), height=Inches(pdf_img_height / Pt(72)))

#                 os.remove(image_path)

#         pdf_writer.save(pdf_path)

# # 输入文件夹路径
# input_folder_path = r"D:\2023fall_HCI\study-compass\pptx"

# # 输出文件夹路径
# output_folder_path = r"D:\2023fall_HCI\study-compass\pptx"

# # 创建 pdf 子文件夹
# pdf_folder_path = os.path.join(output_folder_path, 'pdf')
# if not os.path.exists(pdf_folder_path):
#     os.makedirs(pdf_folder_path)

# # 调用函数进行转换
# convert_docx_to_pdf(input_folder_path, output_folder_path)
# convert_ppt_to_pdf(input_folder_path, output_folder_path)

# test
# if __name__ == "__main__":
#     filePath = r"D:\2023fall_HCI\study-compass\pptx"
#     any2pdf(filePath)