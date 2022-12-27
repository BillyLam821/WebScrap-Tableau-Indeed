import time
import re
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

start_time = time.time()
PATH = "chromedriver"
driver = webdriver.Chrome(PATH)
search_title = "data engineer"
search_title = search_title.replace(" ", "+")
search_location = "canada"
driver.get(f"https://ca.indeed.com/{search_title}-jobs-in-{search_location}")


def get_salary_range():
    salary_href = driver.find_element(By.ID, "filter-salary-estimate-menu").find_elements(By.CLASS_NAME, "yosegi-FilterPill-dropdownListItemLink")
    salary_range = []
    for salary in salary_href:
        each_salary = re.search("\$[\d,]+", salary.get_attribute("href")).group(0)
        salary_url = salary.get_attribute("href")
        # salary_cnt = salary.get_attribute("innerText")
        salary_range.append((each_salary, salary_url))
    return salary_range


def get_industry_list():
    industry_href = driver.find_element(By.ID, "filter-taxo2-menu").find_elements(By.CLASS_NAME, "yosegi-FilterPill-dropdownListItemLink")
    industry_list = []
    for industry in industry_href:
        each_industry = industry.get_attribute("innerText").split(" (")[0]
        industry_url = industry.get_attribute("href")
        industry_list.append((each_industry, industry_url))
    return industry_list

def get_jobID_current_page():
    result_box = driver.find_elements(By.CLASS_NAME, "resultContent")
    job_id_range = []
    for result in result_box:
        job_id = result.find_element(By.TAG_NAME, "a").get_attribute("id")
        job_href = result.find_element(By.TAG_NAME, "a").get_attribute("href")
        job_location = result.find_element(By.CLASS_NAME, "companyLocation").get_attribute("innerHTML").split("<span")[0].replace("Remote in ", "").replace("Hybrid remote in ", "") # some locations have span
        job_id_range.append((job_id, job_href, job_location))
    return job_id_range


def get_next_page():
    try:
        page_nav = driver.find_elements(By.CLASS_NAME, "e8ju0x50")
        if page_nav[-1].get_attribute("aria-label") == "Next Page":
            return page_nav[-1].get_attribute("href")
        else:
            return None
    except:
        return None


def get_job_details():
    each_title = driver.find_element(By.CLASS_NAME, "jobsearch-JobInfoHeader-title").text.replace("- job post", "").strip()
    each_company = driver.find_elements(By.CLASS_NAME, "jobsearch-InlineCompanyRating-companyHeader")[1].text
    each_jd = []
    jd = driver.find_element(By.CLASS_NAME, "jobsearch-jobDescriptionText").find_elements(By.TAG_NAME, "li")
    for j in jd:
        each_jd.append(j.get_attribute("innerText"))
    return each_title, each_company, each_jd


salary_range = get_salary_range()
today = str(date.today())
df = pd.DataFrame(columns=["date", "job_id", "location", "industry", "title", "company", "salary", "description"])


# loop thru pages by salary range in descending order
# because they will be included in lower range
# e.g. $80k+ jobs will be included in $60k+ category
job_id_tracker = []
for salary in reversed(salary_range):
    driver.get(salary[1])
    time.sleep(2) # prevent bot detections
    industry_list = get_industry_list()

    for industry in industry_list:
        driver.get(industry[1])
        time.sleep(2) # prevent bot detections
        
        next_page = get_next_page()

        while next_page != None:

            job_ids = get_jobID_current_page()
            
            for job_id in job_ids:
                # skip if job has been recorded
                if job_id in job_id_tracker:
                    continue
                else:
                    job_id_tracker.append(job_id[0])
                    driver.get(job_id[1])
                    time.sleep(2) # prevent bot detections
                    each_title, each_company, each_jd = get_job_details()
                    df.loc[(len(df))] = [today, job_id[0], job_id[2], industry[0], each_title, each_company, salary[0], each_jd]

            next_page = get_next_page()

df.to_json(f"indeed_{today}.json")
print(f"The script took {round((time.time() - start_time) / 60.0, 2)} minutes to complete")