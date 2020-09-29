import xlwt
import openpyxl
import os
import datetime
import shutil
import json
import csv

from app.myglobals import logfolder, appfolder 

def gen_csv(tableclass, filename):
    # 1.prepare table heads
    tablename = tableclass.__tablename__
    heads_raw = db_mysql.metadata.tables.get(tablename).c
    heads = list()
    for item in heads_raw:
        heads.append(str(item).replace(tablename+'.','',1))
    # 2.prepare table data
    datas = tableclass.query.all()
    # 3.prepare csv writer
    f = open(filename, 'w')
    csv_writer = csv.writer(f)
    # 4. insert table head row
    csv_writer.writerow(heads)
    # 5.insert data rows
    for data in datas:
        data_dict = data.__dict__
        data_dict.pop('_sa_instance_state')
        data_dict.update({'datetime': data_dict.get('datetime').strftime('%Y-%m-%d %H:%M:%S')})
        data_list = list(data_dict.values())
        # todo: sort data_list
        csv_writer.writerow(data_list)
    # 6.save
    f.close()

def gen_excel(tableclass, filename):
    # 1.prepare table heads
    tablename = tableclass.__tablename__
    heads_raw = db_mysql.metadata.tables.get(tablename).c
    heads = list()
    for item in heads_raw:
        heads.append(str(item).replace(tablename+'.','',1))
    # 2.prepare table data
    datas = tableclass.query.all()
    # 3.prepare excel object
    book = openpyxl.Workbook()
    sheet1 = book.create_sheet(index=0, title='sheet1')
    # 4. insert table head row
    # diff with xlwt, openpyxl row start at least 1
    row = 1
    for col,field in enumerate(heads):
        # sheet1.write(0, col, field)
        sheet1.cell(row, col+1).value = field
    # 5.insert data rows
    row += 1
    for data in datas:
        col = 0
        while col < len(heads):
            cell = data.__dict__.get(heads[col])
            if heads[col] == 'datetime':
                cell = cell.strftime('%Y-%m-%d %H:%M:%S')
            # sheet1.write(row, col, cell)
            # diff with xlwt, openpyxl col start at least 1
            sheet1.cell(row, col+1).value = cell
            col += 1
        row += 1
    # 6.save
    book.save(filename)

def gen_excel_legacy(tableclass, filename):
    # 1.prepare table heads
    # heads_raw = db_mysql.metadata.tables.get('testdatas').c
    tablename = tableclass.__tablename__
    heads_raw = db_mysql.metadata.tables.get(tablename).c
    heads = list()
    for item in heads_raw:
        # heads.append(str(item).replace('testdatas.','',1))
        heads.append(str(item).replace(tablename+'.','',1))
    # 2.prepare table data
    # datas = Testdata.query.all()
    datas = tableclass.query.all()
    # 3.prepare excel object
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('sheet1')
    # todo
    # dateFormat = xlwt.XFStyle()
    # dateFormat.num_format_str = '%y-%m-%d %h:%m:%s'
    # dateFormat.num_format_str = 'yyyy/mm/dd'
    # 4. insert table head row
    for col,field in enumerate(heads):
        sheet1.write(0, col, field)
    # 5.insert data rows
    row = 1
    for data in datas:
        col = 0
        while col < len(heads):
            cell = data.__dict__.get(heads[col])
            if heads[col] == 'datetime':
                cell = cell.strftime('%Y-%m-%d %H:%M:%S')
            sheet1.write(row, col, cell)
            col += 1
        row += 1
    # 6.save
    # timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # filename = 'testdatas-' + timestamp + '.xls'
    # filename = os.path.join(topdir, 'updownload', filename)
    book.save(filename)

# please be very careful to call this function
def empty_folder(folder):
    files = os.listdir(folder)
    for file in files:
        if file == '.gitkeep':
            continue
        file = os.path.join(folder, file)
        # todo
        # if file type is folder, here will raise IsADirectoryError
        os.remove(file)

def empty_dir(path):
    for root, dirs, files in os.walk(path, topdown=False):
        # print('==root==', root)
        for name in files:
            # print('==file==', name)
            if name =='.gitkeep':
                continue
            os.remove(os.path.join(root, name))
        for name in dirs:
            # print('==dir==', name)
            # os.removedirs(os.path.join(root, name))
            os.rmdir(os.path.join(root, name))

def rm_pycache(path):
     for root, dirs, files in os.walk(path, topdown=False):
        for name in dirs:
            if name == '__pycache__':
                # os.removedirs(os.path.join(root, name))
                shutil.rmtree(os.path.join(root, name))


def cleanup_log():
    empty_dir(logfolder)

def cleanup_pycache():
    rm_pycache(appfolder)

def write_json_to_file(o_dict, filename):
    with open(filename, 'w') as f:
        json.dump(o_dict, f, indent=4)

def read_textfile_oneline(filename):
    content = open(filename).readline()
    content = content.replace('\r', '').replace('\n','')
    return content
