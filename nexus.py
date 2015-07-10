import time
import re
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


red_light = "    --> Checkpoint: \033[31mRED\033[0m"
green_light = "    --> Checkpoint: \033[32mGREEN\033[0m"


class Nexus(object):
    def __init__(self, case_browser, case_hub, case_target):
        self.driver = None
        self.case_browser = None
        self.case_hub = case_hub
        self.case_target = None
        hub_fields = case_hub.split("=")
        self.target_hub, self.identify_hub = hub_fields
        self.wait = 0

        capability_dictionary = {
            "FIREFOX": webdriver.DesiredCapabilities.FIREFOX.copy(),
            "INTERNETEXPLORER": webdriver.DesiredCapabilities.INTERNETEXPLORER.copy(),
            "CHROME": webdriver.DesiredCapabilities.CHROME.copy(),
            "SAFARI": webdriver.DesiredCapabilities.SAFARI.copy(),
            "MOBILE": webdriver.DesiredCapabilities.FIREFOX.copy()
        }

        self.browser = capability_dictionary[case_browser]
        self.driver = webdriver.Remote(self.target_hub, self.browser)

        self.log("{0} driver acquired from grid: {1}".format(self.identify_hub, self.target_hub))

    def __del__(self):
        self.log("{0} driver released".format(self.identify_hub))
        self.driver.quit()

    def log(self, *messages):
        print("\033[32m **", *messages, end="")
        print(" **\033[0m\n")

    def execute_test(self, explicit_wait, action_identifier, action_type, action_on, action_by, action_text, action_screenshot, action_pause):
        self.wait = explicit_wait
        output = "    --> {0}: {1}".format(action_type, action_identifier)
        if action_type == "start_url":        
            result = self.driver.get(action_text)
        elif action_type == "click_element" or action_type == "standard_keys" or action_type == "special_keys" or action_type == "key_chords":
            result = self.do_action(action_type, action_on, action_by, action_text)
        elif action_type == "check_condition" or action_type == "check_content" or action_type == "check_url" or action_type == "check_title":
            result = self.do_assert(action_type, action_on, action_by, action_text)
        elif action_type == "switch_frame":
            result = self.switch_frame(action_text)
        elif action_type == "write_database_variable" or action_type == "write_screen_variable" or action_type == "read_variable":
            result = self.use_variable(action_identifier, action_type, action_on, action_by, action_text)
        elif action_type == "get_url":
            result = self.driver.navigate.to(action_text)
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (execute_test method)")

        if result is not None:
            output += "\n" + result

        time.sleep(float(action_pause))

        if action_screenshot == "Y":
            as_fields = self.case_hub.split("=")
            as_hub, as_target = as_fields
            self.driver.save_screenshot('' + as_target + '_' + action_identifier + '.png')

        return output

    def do_assert(self, action_type, action_on, action_by, action_text):
        if action_type == "check_condition":
            check_condition = self.locate_element(action_on, action_by)
            if str(check_condition) == "FAILURE":
                return red_light
            else:
                return green_light
        elif action_type == "check_content":
            check_content = self.locate_element(action_on, action_by).text
            if action_text not in check_content:
                return red_light
            else:
                return green_light
        elif action_type == "check_url":
            check_url = str(self.driver.current_url)
            if action_text != check_url:
                return red_light
            else:
                return green_light
        elif action_type == "check_title":
            check_title = str(self.driver.title)
            if action_text != check_title:
                return red_light
            else:
                return green_light
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (do_assert method)")

    def do_action(self, action_type, action_on, action_by, action_text):
        execute_action = self.locate_element(action_on, action_by)
        if action_type == "click_element":
            execute_action.click()
        elif action_type == "standard_keys":
            if "<RIG>" not in action_text:
                execute_action.send_keys(action_text)
            else:
                rdg_fields = action_text.split(",")
                rdg_tag, rdg_length, rdg_characters = rdg_fields
                execute_action.send_keys(self.generator(rdg_length, rdg_characters))
        elif action_type == "special_keys":
            special_dictionary = {
                "BACK_SPACE": Keys.BACK_SPACE
            }
            execute_action.send_keys(special_dictionary[action_text])
        elif action_type == "key_chords":
            chord_dictionary = {
                "ALT": Keys.ALT,
                "COMMAND": Keys.COMMAND,
                "SHIFT": Keys.SHIFT,
                "CONTROL": Keys.CONTROL
            }
            key_sequence = ""
            key_chords = action_text.split(",")
            for key_chord in key_chords:
                if key_chord in chord_dictionary.keys():
                                key_sequence += chord_dictionary[key_chord] + ", "
                else:
                    key_sequence += key_chord + ", "
            execute_action.send_keys(key_sequence.rstrip(", "))
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (do_action method)")

    def locate_element(self, action_on, action_by):
        action_by_dictionary = {
            "id": By.ID,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "xpath": By.XPATH,
            "tag_name": By.TAG_NAME,
            "class_name": By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
            "name": By.NAME
        }
        try:
            action = WebDriverWait(self.driver, float(self.wait)).until(EC.presence_of_element_located((action_by_dictionary[action_by], action_on)))
            return action
        except TimeoutException:
            return "FAILURE"

    def use_variable(self, action_identifier, action_type, action_on, action_by, action_text):
        if action_type == "write_database_variable":
            on_fields = action_on.split(",")
            database_user, database_password, database_host, database_name = on_fields
            try:
                database_connection = self.mysql_connection(database_user, database_password, database_host, database_name)
                cursor = database_connection.cursor()
                query = action_by
                cursor.execute(query)
                for (action_text) in cursor:
                    transformed_string = str(action_text)
                    sanitised_string = transformed_string.strip("('").strip("',)")
                    self.write_file(action_identifier, sanitised_string, "DB")
                cursor.close()
                database_connection.close()
            except:
                print(red_light + " (Database Error)")
        elif action_type == "write_screen_variable":
            write_screen_variable = re.search(action_text, self.locate_element(action_on, action_by).text)
            if write_screen_variable:
                self.write_file(action_identifier, write_screen_variable.group(0), "UI")
            else:
                return red_light + " (" + action_text + " Not Located"
        elif action_type == "read_variable":
            read_variable = self.read_file(action_text)
            self.do_action("standard_keys", action_on, action_by, read_variable)
        else:
            raise Exception("Action Type: " + action_type + " not defined in nexus.py file (use_variable method)")

    def write_file(self, action_identifier, sanitised_string, action_variable):
        with open('' + action_identifier, 'wt') as reusable_file:
            reusable_file.write(str(sanitised_string))

    def read_file(self, file_name):
        with open('' + file_name, 'rt') as contents:
            for content in contents:
                return content

    def mysql_connection(self, database_user, database_password, database_host, database_name):
        default_connection = {
            'user': database_user,
            'password': database_password,
            'host': database_host,
            'database': database_name
        }
        connection = mysql.connector.connect(**default_connection)
        return connection

    def switch_frame(self, action_text):
        if action_text != "defaultContent":
            self.driver.switch_to.frame(action_text)
        else:
            self.driver.switch_to.default_content()

    def generator(self, rdg_length, rdg_characters):
        return ''.join(random.choice(rdg_characters) for _ in range(int(rdg_length)))
