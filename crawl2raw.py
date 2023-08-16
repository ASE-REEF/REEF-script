# 本文件用于把patch crawl的文件 中source code 找到并下载

import os
import urllib.request
import json
from tqdm import tqdm


def fetch_patchs(Year='2023', Month='1'):
    patches_id = 0 # every file patch id is unique
    files_id = 0
    YM = Year+'_'+Month
    patch_name = 'crawl_result/' + YM + '_patch.jsonl'
    rawcode_name = 'rawcode_result/' + YM + '_rawcode.jsonl'
    error_file = 'rawcode_result/' + YM + '_rawcode_error.txt'

    already_patch = 0
    if os.path.exists(rawcode_name):
        with open(rawcode_name, "r", encoding = "utf-8") as rf:
            alcon = rf.readlines()
            if len(alcon) > 0:
                last = alcon[-1]
                already_patch = int(json.loads(last)['patches_id'])
    print("already_patch: ", already_patch)
    patches= []
    with open(patch_name, "r", encoding="utf-8") as f:
        patches = json.load(f)

    """ Here is the explanation for the code above:
    1. The fetch_patchs function is used to fetch the data from the "crawl_result" folder and save them to the "rawcode_result" folder.
    2. The function takes two parameters, Year and Month, to specify the data to be processed.
    3. First, we initialize two variables: "patches_id" and "files_id", which are used to identify the unique id of each data.
    4. Then, we initialize the names of the files to be read and written.
    5. We check if the file to be written already exists. If it exists, we read the last line of the file and get the id of the last data. We will use this id to determine where to start writing.
    6. Then, we read the file to be read and save the data in the list "patches". 
    """

    errors = []

    for patch in tqdm(patches):
        patches_id += 1
        if patches_id <= already_patch:
            continue
        for eachfile in patch['files']:
            try:
                if "raw_url" in eachfile:
                    files_id += 1
                    one_res = {}
                    raw_url = eachfile['raw_url']
                    # "status": "removed", it could be possible that the file has changed but the content is the same
                    if 'patch' not in eachfile:
                        continue
                    patch = eachfile['patch']
                    # download the web content
                    response = urllib.request.urlopen(raw_url)
                    content = response.read()
                    if content!=None:
                        one_res['patches_id'] = patches_id
                        one_res['files_id'] = files_id
                        one_res['language'] = eachfile['filename'].split('.')[-1]
                        one_res['raw_url'] = raw_url  # url for identification
                        one_res['raw_code'] = str(content,encoding='utf-8') # raw code
                        one_res['patch'] = patch
                    with open(rawcode_name, 'a', encoding='utf-8') as f2:
                        jsonobj = json.dumps(one_res)
                        f2.write(jsonobj + '\n')
                else:
                    print("Wrong! raw_url not exist, see case ", patches_id)
                    errors.append(patches_id) 
            except Exception as e:
                print(e)
                print("case is wrong ", patches_id)
                continue
 
                
    with open(error_file, "w", encoding = "utf-8") as rf:
        for err in errors:
            rf.write(err+'\n')
    print('in total we have got {}'.format(patches_id))


def main():
    Year = '2022'
    Month = '2'

    Years = ['2023','2022','2021','2020','2019','2018','2017','2016']

    Months = [str(i) for i in range(1, 13)]

    for Year in Years:
        for Month in Months:
            fetch_patchs(Year, Month)

if __name__ == '__main__':
    main()
