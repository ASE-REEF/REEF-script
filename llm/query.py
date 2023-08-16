from qwen import chat_single_qwen
import pandas as pd
import json
import random
import re
import os
import copy
import time
from itertools import groupby
from http import HTTPStatus
from tqdm import tqdm



def query():
    file_path = r'../merge_result'
    language = 'C++'
    file_name = file_path + '/merge_' + language + '.jsonl' # merge_C++
    outputfile = './test_result/query' + '_'+ language + '.jsonl'
    Max_patch = 2000*5 
    result_filename = outputfile
    already_query = 0
    OSL = False
    if os.path.exists(result_filename):
        with open(result_filename, 'r', encoding='utf-8') as f:
            already_query = len(f.readlines())
    print('already query: ', already_query)

    # patches = json.load(f)

    with open(file_name, "r",encoding = "utf-8") as r:
        content = r.readlines()
        for i in range(len(content)):
            each = content[i]
            if i < already_query:
                continue

            record_dict = json.loads(each)
            CWEs = record_dict['CWEs'] # list
            CWE_info = CWEs[0] if len(CWEs) > 0 else ''
            ori_message = record_dict['origin_message']
            details = record_dict['details']
            patches_list = []
            total_patch_len = 0
            if len(details) > 0:
                for detail in details:
                    patches_list.append(detail['patch'])
                    if total_patch_len > Max_patch:
                        break
                    total_patch_len += len(detail['patch'])
            # 收集完成构造prompt
            system_message = '''You are a professional developer that works on writing explanation for CVEs.  \
            You are first given a CVE with CWE information, and commit message. Note that this message may be misleading and you \
            are trying to write a more clear and concise one. Then you are given the detail patches for the CVE. Note that one CVE may have multiple patches as it may change \
            many files and codes.'''
            
            prompt = system_message + ' ' + '[CWE information]: ' + CWE_info + ' ' + '[commit message]: ' + ori_message + ' ' + '[Patches]: '
            if OSL: 
                exp_cwe,exp_ori_message,exp_patches,exp_ans = '', '', '', '' # TODO 
                example = '[Example CWE information]: ' + exp_cwe + ' [Example commit message]: ' + exp_ori_message + ' ' + '[Example Patches]: '+ exp_patches + ' ' + '[Example answer]: ' + exp_ans
                prompt = system_message + example + '[CWE information]: ' + CWE_info + ' ' + '[commit message]: ' + ori_message + ' ' + '[Patches]: '
            for i in range(len(patches_list)):
                addprompt= f'[patch {i+1} start]: ' + patches_list[i] + '\n' + f'[patch {i+1} end]: ' + '\n'
                prompt += addprompt
            
            answer_prompt = '''\nYour explanation should accurately describe how patch fixes potential vulnerability, including \
# the functions that mainly involved. Answer this in one sentence less than 30 words.'''
            prompt += answer_prompt
            print('prompt is: ', prompt)
            q_content = prompt
            Max_try = 5
            tried = 0
            got_ans = False
            answer = ''

            try:
                while tried < Max_try and not got_ans:
                    answer = ''
                    response = chat_single_qwen(q_content, bot='qwen-plus-beta-v1')
                    if response.status_code == HTTPStatus.OK:
                        got_ans = True
                        answer = response.output.text
                        print('answer is ',answer)
                    else:
                        print('Code: %d, status: %s, message: %s' % (response.status_code, response.code, response.message))
                        with open('./log.txt', 'a', encoding='utf-8') as f:
                            f.write('error!'+ response.message+'__content is: ' + q_content + '\n')
                        tried += 1

                if not got_ans:
                    print('-------------fail, please check ', q_content)

                if answer != '' :
                    record_dict['LLM_message'] = answer
                    with open(result_filename, 'a', encoding='utf-8') as f2:
                        jsonobj = json.dumps(record_dict, ensure_ascii=False)
                        f2.write(jsonobj + '\n')
            except Exception as e:
                print(e)

    return 1


def main():
    query()

main()