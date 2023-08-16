import os
import urllib.request
import json
from tqdm import tqdm


def merge_alldata(Year='2023', Month='1',index = 0, total = 0):
    YM = Year+'_'+Month
    CVEinfo_name = 'results/' + YM + '.jsonl'
    patch_name = 'crawl_result/' + YM + '_patch.jsonl'
    patcherr_name = 'crawl_result/' + YM + '_patch_error.txt'
    rawcode_name = 'rawcode_result/' + YM + '_rawcode.jsonl'
    mergefile = 'merge_result/merge_'

    CVEinfo = []
    with open(CVEinfo_name, "r", encoding = "utf-8") as rf:
        for line in rf:
            CVEinfo.append(json.loads(line))
    patches = []
    with open(patch_name, "r", encoding="utf-8") as f:
        patches = json.load(f)
    rawcode = []
    with open(rawcode_name, "r", encoding = "utf-8") as rfc:
        for line in rfc:
            rawcode.append(json.loads(line))
    patch_err = []
    with open(patcherr_name, "r", encoding = "utf-8") as rfc:
        for line in rfc:
            patch_err.append(line.replace('\n', ''))

    patch_id = 0
    CVEinfo_id = 0
    debug = 0
    while CVEinfo_id < len(CVEinfo) and patch_id < len(patches):
        for resource in CVEinfo[CVEinfo_id]['resources']:
            repo1 = (patches[patch_id]['html_url'].partition('github.com/')[2].partition('/commit'))[0]
            repo2 = (resource.partition('github.com/')[2].partition('/commit'))[0]
            url = resource.replace('/commit/', '/commits/').replace('https://github.com/', 'https://api.github.com/repos/')
            if 'commit' in resource and url not in patch_err and repo1.lower() == repo2.lower():
                merge_data = {} 
                merge_data['index'] = index
                merge_data['cve_id'] = CVEinfo[CVEinfo_id]['cve_id']
                merge_data['CWEs'] = CVEinfo[CVEinfo_id]['CWEs']
                merge_data['language'] = CVEinfo[CVEinfo_id]['language']
                merge_data['cvss'] = CVEinfo[CVEinfo_id]['cvss']
                merge_data['message'] = patches[patch_id]['message']
                merge_data['url'] = patches[patch_id]['url']
                merge_data['html_url'] = patches[patch_id]['html_url']
                merge_data['details'] = []
                # 遍历当前patch_result的多个files
                for eachfile in patches[patch_id]['files']:
                    # 寻找当前file对应的多个rawcode_id
                    for rawcode_id in range(len(rawcode)):
                        if rawcode[rawcode_id]['patches_id'] == patch_id+1 and rawcode[rawcode_id]['raw_url'] == eachfile['raw_url']:
                            detail = {}
                            detail['raw_url'] = eachfile['raw_url']
                            detail['raw_code'] = rawcode[rawcode_id]['raw_code']
                            detail['patch'] = eachfile['patch']
                            detail['semgrep_result'] = " "
                            merge_data['details'].append(detail)
                            total += 1
                            break
                if merge_data['details']:
                    merge_name = mergefile + merge_data['language'] + '.jsonl'
                    with open(merge_name, 'a', encoding='utf-8') as f2:
                        jsonobj = json.dumps(merge_data, indent=4)
                        f2.write(jsonobj + '\n')
                    index += 1  # 写入一数据后再 增加index  
                patch_id += 1
                if patch_id >= len(patches):
                    break
        CVEinfo_id += 1

    return index,  total
        
def main():

    Years = ['2022','2021','2020','2019','2018','2017','2016']
    Months = [str(i) for i in range(1, 13)]

    index = 0
    total = 0
    for Year in Years:
        for Month in Months:
            index, total = merge_alldata(Year, Month, index, total)
        print(str(index) + ' ' + str(total))
    print('in total we merge '+str(index)+' commits')
    print('in total we merge '+str(total)+' rawcodes')
    

if __name__ == '__main__':
    main()