from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
import re
import os
import json
import time
import random



def runone(Year, Month):
    YM = Year + '_' + Month
    filename = 'logs/' + YM + '.log'
    res_filename = 'results/' + YM + '.jsonl'

    if not os.path.exists(filename):
        driver = webdriver.Chrome(ChromeDriverManager().install())
        url = "https://www.mend.io/vulnerability-database/full-listing/"+Year+"/"+Month # target URL
        #  please install ChromeDriver and add them into the environment variable
        driver.get(url)
        wait = WebDriverWait(driver, 3)
        links = []

        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        try:
            max_pagenumber = int(soup.find_all("li", class_="vuln-pagination-item")[-2].text.strip())
        except Exception as e:
            max_pagenumber = 1
        """ The code above does the following, explained in English:
        1. Open the URL
        2. Get the HTML code of the URL
        3. Convert the HTML code to a format that BeautifulSoup can understand
        4. Find all the elements that have the class "vuln-pagination-item"
        5. Get the second to last element of the list of elements that have the class "vuln-pagination-item"
        6. Get the text from the second to last element of the list of elements that have the class "vuln-pagination-item"
        7. Remove any trailing or leading spaces from the text
        8. Convert the text to an integer
        9. Assign the integer to the variable max_pagenumber """

        for link in soup.find_all("a", href=re.compile("^/vulnerability-database/CVE")):
            name = link.text
            href = link.get("href")
            links.append((name, href))
        if max_pagenumber > 1:
            # go through all the pages
            for i in range(2,max_pagenumber+1):

                url = "https://www.mend.io/vulnerability-database/full-listing/"+Year+"/"+ Month + '/'+str(i)
                driver.get(url)
                wait = WebDriverWait(driver, 3)
                soup = BeautifulSoup(driver.page_source, "html.parser")

                for link in soup.find_all("a", href=re.compile("^/vulnerability-database/CVE")):
                    name = link.text
                    href = link.get("href")
                    links.append((name, href))
        print(links)
        print('number of possible cve list is {}'.format(len(links)))

        with open(filename,'w') as f:
            for name, href in links:
                f.write(href+'\n')
    # read it
    with open(filename,'r') as f:
        content = f.readlines()
    prefix = 'https://www.mend.io'

    max_num = 1  # test for 1

    already_query_qid = 0
    if os.path.exists(res_filename):
        with open(res_filename, 'r', encoding='utf-8') as f2:
            queried = f2.readlines()
            already_query_qid = json.loads(queried[-1])["q_id"] if len(queried) != 0 else 0
            print('already query {}'.format(already_query_qid))
    # we define a variable `already_query_qid` to record the last query q_id, since we have queried for the data before, we need to record the last time of the query and continue to query the following data 
    driver = webdriver.Chrome(ChromeDriverManager().install())

    for i in range(len(content)):
        try:
            random_time = random.uniform(0.1, 1)
            # time.sleep(random_time) # sleep
            one_res = {"cve_id": content[i].strip().split('/')[-1], "language":None, "date":None, "resources": [], "CWEs": [] ,"cvss": None, "q_id":i }
            if i < already_query_qid:
                continue

            fullweb_url = prefix + content[i].strip()
            driver.get(fullweb_url)
            wait = WebDriverWait(driver, 3)
            soup = BeautifulSoup(driver.page_source, "html.parser")

            for tag in soup.find_all(["h4", "p"]):
                if tag.name == "h4":
                    if "Date:" in tag.text:
                        date = tag.text.strip().replace("Date:", "").strip()

                    elif "Language:" in tag.text:
                        language = tag.text.strip().replace("Language:", "").strip()
            one_res["date"] =  date
            one_res["language"] =  language

            reference_links = []
            for div in soup.find_all("div", class_="reference-row"):
                for link in div.find_all("a", href=True):
                    if "github.com" in link["href"]:
                        reference_links.append(link["href"])
            one_res["resources"] =  reference_links


            severity_score = ""
            div = soup.find("div", class_="ranger-value")
            if div:
                label = div.find("label")
                if label:
                    severity_score = label.text.strip()
            one_res["cvss"] =  severity_score

            cwe_numbers = []
            for div in soup.find_all("div", class_="light-box"):
                for link in div.find_all("a", href=True):
                    if "CWE" in link.text:
                        cwe_numbers.append( link.text)
            one_res["CWEs"] =  cwe_numbers

            if (one_res["cve_id"] is not None) and (one_res["language"] is not None) and (one_res["date"] is not None) and ( \
                    one_res["resources"] != []) and (one_res["CWEs"] != []) and (one_res["cvss"] is not None):
                print("correct! all infor is done for case", content[i])

                with open(res_filename, 'a', encoding='utf-8') as f2:
                    jsonobj = json.dumps(one_res)
                    f2.write(jsonobj + '\n')
            else:
                # print('--------------')
                if one_res["resources"] == []:
                    print('no source ,therefore give it up ',content[i])
                else:
                    print("Wrong! At least one item in one_res is empty, see case ",content[i])
                # print('--------------')
        except Exception as e:
            print('fail website is {}'.format(fullweb_url))
            print(e)

    driver.quit()  # close it


""" Here is the explanation for the code following:
1. We define a function called main. The code in this function will be executed when we run the script.
2. We define the variables called Year and Month. We will use these variables to get the data for each month.
3. We define a list called Years. This list contains all the years we want to get data for.
4. We define a list called Months. This list contains all the months we want to get data for.
5. We use a for loop to iterate through all the years in the Years list.
"""

def main():
    Year = '2022'
    Month = '2'

    Years = ['2015','2014','2013','2012','2011','2010']
    Months = [str(i) for i in range(1, 13)]

    for Year in Years:
        for Month in Months:
            runone(Year, Month)

if __name__ == '__main__':
    main()