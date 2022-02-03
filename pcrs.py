from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

settings = json.load(open('settings.json'))
driver = webdriver.Chrome(ChromeDriverManager().install())
# scope the search to https://pcrs.teach.cs.toronto.edu/csc209-2022-01/problems/multiple_choice/(some number)/run using regex
driver.scopes = [
    'https://pcrs.teach.cs.toronto.edu/csc209-2022-01/problems/multiple_choice/[0-9]+/run'
]
driver.get(settings['base_pcrs'])
driver.find_element(by=By.XPATH, value='//*[@id="username"]').send_keys(settings['username'])
driver.find_element(by=By.XPATH, value='//*[@id="password"]').send_keys(settings['password'])
driver.find_element(by=By.XPATH, value='/html/body/div/div/div[1]/div[2]/form/button').click()
time.sleep(4)
driver.get(settings['url'])
questions = driver.find_elements(by=By.XPATH, value="//*[contains(@id, 'multiple_choice-')]")
questions = [q for q in questions if q.get_attribute('id').startswith('multiple_choice-')]
for question in questions:
    del driver.requests
    curr_prob = []
    current_url = f"{settings['base_pcrs']}problems/multiple_choice/{question.get_attribute('id').split('-')[-1]}/run"
    # get all checkboxes for this question
    boxes = driver.find_elements(by=By.XPATH, value=f"//*[@id='{question.get_attribute('id')}']//input[@type='checkbox']")
    for box in boxes:
        # iterate and submit each answer
        box.click()
        driver.find_element(by=By.XPATH, value=f"//*[@id='{question.get_attribute('id')}']//*[@id='submit-id-submit']").click()
        time.sleep(0.3)
        # after submission check for cookie response and see the result of the question, and then uncheck the box
        box.click()
    for request in driver.requests:
        if request.response:
            # convert request to json object
            curr_prob.append(json.loads(decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity')).decode('utf-8')))
    prob_max = 0
    print(curr_prob)
    for prob in curr_prob:
        if prob['score'] > prob_max:
            prob_max = prob['score']
    box_indices = []
    for i, prob in enumerate(curr_prob):
        if prob['score'] == prob_max:
            box_indices.append(i)
    boxes = driver.find_elements(by=By.XPATH, value=f"//*[@id='{question.get_attribute('id')}']//input[@type='checkbox']")
    print(box_indices)
    for i in box_indices:
        boxes[i].click()
    driver.find_element(by=By.XPATH, value=f"//*[@id='{question.get_attribute('id')}']//*[@id='submit-id-submit']").click()
    time.sleep(0.3)

time.sleep(20)