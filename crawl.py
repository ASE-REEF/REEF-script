import json
import time
import subprocess

"""
This code is a Python script that fetches patch information from GitHub API for a list of CVEs (Common Vulnerabilities and Exposures) obtained from a JSON file. The script iterates through a range of years and months, and for each month, it fetches patch information for the corresponding CVEs using the GitHub API. The fetched information is stored in a JSON file, and any errors encountered during the process are recorded in a separate text file. The script uses subprocess and time modules to interact with the GitHub API and maintain a rate limit of 1 request per second. 
"""


# notice that you should add your github api in "Authorization: Bearer TODO"

def fetch_patchs(Year='2023', Month='1'):
    
    YM = Year+'_'+Month
    res_filename = 'results/' + YM + '.jsonl'
    patch_name = 'crawl_result/' + YM + '_patch.jsonl'
    error_file = 'crawl_result/' + YM + '_patch_error.txt'

    CVES = [json.loads(line) for line in open(res_filename, "r",encoding = "utf-8")]
    querys = []
    fetchs = []
    for CVE in CVES:
        for res in CVE['resources']:
            if "commit" in res:
                querys.append(res.replace('/commit/', '/commits/').replace('https://github.com/', 'https://api.github.com/repos/'))
    try:
        total = len(querys)
        i = 0
        errors = []
        for query in querys:
            i += 1
            print('***************'+str(i)+'/'+str(total)+'***************')
            data = {}
            try:
                output = bytes.decode(subprocess.check_output(["curl", "--request", "GET" ,"-H", "Authorization: Bearer TODO", "-H", "X-GitHub-Api-Version: 2022-11-28", "-u", "KEY:", query]))

                data = json.loads(output)
            except Exception as e:
                print(e)
                continue
            if 'url' in data and 'html_url' in data and 'commit' in data and 'files' in data:    
                fetchs.append({
                    'url': data['url'],
                    'html_url': data['html_url'],
                    'message': data['commit']['message'],
                    'files': data['files']
                })
            else:
                print("Wrong! Data is NULL, see case ", query)
                print(data)
                errors.append(query)    
            time.sleep(1)
    except Exception:
        with open(patch_name, "w", encoding = "utf-8") as rf:
            rf.write(json.dumps(fetchs, sort_keys=True, indent=4, separators=(',', ': ')))
    except KeyboardInterrupt:
        with open(patch_name, "w", encoding = "utf-8") as rf:
            rf.write(json.dumps(fetchs, sort_keys=True, indent=4, separators=(',', ': ')))
    
    with open(patch_name, "w", encoding = "utf-8") as rf:
        rf.write(json.dumps(fetchs, indent=4, separators=(',', ': ')))
    with open(error_file, "w", encoding = "utf-8") as rf:
        for err in errors:
            rf.write(err+'\n')



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