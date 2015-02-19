import time
import re
import string
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

red_light = "               --> Checkpoint: RED"
green_light = "               --> Checkpoint: GREEN"

class Nexus:

	def engage_driver(case_browser, case_hub, case_target):
		hub_fields = case_hub.split("=")
		target_hub, identify_hub = hub_fields
		print("\n\n" + "   Selenium: Driver Acquired\n" + "   Browser: " + identify_hub + "\n" + "   Grid: " + target_hub)
		capability_dictionary = {
			"FIREFOX":webdriver.DesiredCapabilities.FIREFOX.copy(),
			"INTERNETEXPLORER":webdriver.DesiredCapabilities.INTERNETEXPLORER.copy(),
			"CHROME":webdriver.DesiredCapabilities.CHROME.copy(),
			"SAFARI":webdriver.DesiredCapabilities.SAFARI.copy(),
			"MOBILE":webdriver.DesiredCapabilities.FIREFOX.copy()
		}
		browser = capability_dictionary[case_browser]
		driver = webdriver.Remote(target_hub, browser)
		driver.implicitly_wait(10)
		return driver

	def execute_test(engage_driver, case_hub, explicit_wait, action_identifier, action_type, action_on, action_by, action_text, action_screenshot, action_pause):
		pause = float(action_pause)
		print("         --> Type: " + action_type + "\n" + "            --> Identity: " + action_identifier)
		if action_type == "start_url":		
			engage_driver.get(action_text)
		elif action_type == "click_element" or action_type == "standard_keys" or action_type == "special_keys" or action_type == "key_chords":
			Nexus.do_action(engage_driver, explicit_wait, action_type, action_on, action_by, action_text)
		elif action_type == "check_condition" or action_type == "check_content" or action_type == "check_url" or action_type == "check_title":
			Nexus.do_assert(engage_driver, explicit_wait, action_type, action_on, action_by, action_text)
		elif action_type == "switch_frame":
			Nexus.switch_frame(action_text)
		elif action_type == "write_database_variable" or action_type == "write_screen_variable" or action_type == "read_variable":
			Nexus.use_variable(engage_driver, explicit_wait, action_identifier, action_type, action_on, action_by, action_text)
		elif action_type == "get_url":
			engage_driver.navigate.to(action_text)
		else:
			print("Action Type: " + action_type + " not defined in nexus_object.py file (execute_test method)")
		time.sleep(pause)
		if action_screenshot == "Y":
			as_fields = case_hub.split("=")
			as_hub, as_target = as_fields
			engage_driver.get_screenshot_as_file('' + as_target + '_' + action_identifier+ '.png')

	def release_driver(engage_driver):
		print("   Selenium: Driver Released")
		engage_driver.quit()

	def do_assert(engage_driver, explicit_wait, action_type, action_on, action_by, action_text):
		if action_type == "check_condition":
			check_condition = Nexus.locate_element(engage_driver, explicit_wait, action_on, action_by)
			if str(check_condition) == "FAILURE":
				print(red_light)
			else:
				print(green_light)
		elif action_type == "check_content":
			check_content =  Nexus.locate_element(engage_driver, explicit_wait, action_on, action_by).text
			if action_text not in check_content:
				print(red_light)
			else:
				print(green_light)
		elif action_type == "check_url":
			check_url = str(engage_driver.current_url)
			if action_text != check_url:
				print(red_light)
			else:
				print(green_light)
		elif action_type == "check_title":
			check_title = str(engage_driver.title)
			if action_text != check_title:
				print(red_light)
			else:
				print(green_light)
		else:
			print("Action Type: " + action_type + " not defined in nexus_object.py file (do_assert method)")

	def do_action(engage_driver, explicit_wait, action_type, action_on, action_by, action_text):
		execute_action = Nexus.locate_element(engage_driver, explicit_wait, action_on, action_by)
		if action_type == "click_element":
			execute_action.click()
		elif action_type == "standard_keys":
			if "<RIG>" not in action_text:
				execute_action.send_keys(action_text)
			else:
				rdg_fields = action_text.split(",")
				rdg_tag, rdg_length, rdg_characters = rdg_fields
				execute_action.send_keys(Nexus.generator(rdg_length, rdg_characters))
		elif action_type == "special_keys":
			special_dictionary = {
				"BACK_SPACE":Keys.BACK_SPACE
			}
			execute_action.send_keys(special_dictionary[action_text])
		elif action_type == "key_chords":
			chord_dictionary = {
				"ALT":Keys.ALT,
				"COMMAND":Keys.COMMAND,
				"SHIFT":Keys.SHIFT,
				"CONTROL":Keys.CONTROL
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
			print("Action Type: " + action_type + " not defined in nexus_object.py file (do_action method)")

	def locate_element(engage_driver, explicit_wait, action_on, action_by):
		action_by_dictionary = {
			"id":By.ID, 
			"link_text":By.LINK_TEXT,
			"partial_link_text":By.PARTIAL_LINK_TEXT,
			"xpath":By.XPATH,
			"tag_name":By.TAG_NAME,
			"class_name":By.CLASS_NAME,
			"css_selector":By.CSS_SELECTOR,
			"name":By.NAME
		}
		try:
			action = WebDriverWait(engage_driver, float(explicit_wait)).until(EC.presence_of_element_located((action_by_dictionary[action_by], action_on)))
			return action
		except TimeoutException:
			return "FAILURE"

	def use_variable(engage_driver, explicit_wait, action_identifier, action_type, action_on, action_by, action_text):
		if action_type == "write_database_variable":
			on_fields = action_on.split(",")
			database_user, database_password, database_host, database_name = on_fields
			try:
				database_connection = Nexus.mysql_connection(database_user, database_password, database_host, database_name)
				cursor = database_connection.cursor()
				query = (action_by)
				cursor.execute(query)
				for (action_text) in cursor:
					transformed_string = str(action_text)
					sanitised_string = transformed_string.strip("('").strip("',)")
					Nexus.write_file(action_identifier, sanitised_string, "DB")
				cursor.close()
				database_connection.close()
			except:
				print(red_light + " (Database Error)")
		elif action_type == "write_screen_variable":
			write_screen_variable = re.search(action_text, Nexus.locate_element(engage_driver, explicit_wait, action_on, action_by).text)
			if write_screen_variable:
				Nexus.write_file(action_identifier, write_screen_variable.group(0), "UI")
			else:
				print("               --> Checkpoint: RED (" + action_text + " Not Located")
		elif action_type == "read_variable":
			read_variable = Nexus.read_file(action_text)
			Nexus.do_action(engage_driver, explicit_wait, "standard_keys", action_on, action_by, read_variable)
		else:
			print("Action Type: " + action_type + " not defined in nexus_object.py file (use_variable method)")

	def write_file(action_identifier, sanitised_string, action_variable):
		with open('' + action_identifier, 'wt') as reusable_file:
			reusable_file.write(str(sanitised_string))
			print("               --> Reusable Variable Stored (" + action_variable + "): " + sanitised_string)

	def read_file(file_name):
		with open('' + file_name, 'rt') as contents:
			for content in contents:
				print("               --> Reusable Variable Retrieved: " + content)
				return content

	def mysql_connection(database_user, database_password, database_host, database_name):
		default_connection = {
			'user': database_user,
			'password': database_password,
			'host': database_host,
			'database': database_name
		}
		connection = mysql.connector.connect(**default_connection)
		return connection

	def switch_frame(action_text):
		if action_text != "defaultContent":
			engage_driver.switchTo.frame(action_text)
		else:
			engage_driver.switchTo.defaultContent

	def generator(rdg_length, rdg_characters):
		return ''.join(random.choice(rdg_characters) for _ in range(int(rdg_length)))
