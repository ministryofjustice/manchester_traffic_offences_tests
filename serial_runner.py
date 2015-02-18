import time
from nexus_object import Nexus

class Jam:
	
	def execute_suite(case_file, action_file):
		cases = sys.argv[1]
		browsers = sys.argv[2]
		hubs = sys.argv[3]
		targets = sys.argv[4]
		screenshot = sys.argv[5]
		include = sys.argv[6]
		if include == "Y":
			cases = cases.split(",")
			for case in cases:
				Jam.execute_case(case, browsers, hubs, targets, screenshot, case_file, action_file)
				
	def execute_case(suite_case, suite_browsers, suite_hubs, suite_targets, suite_screenshot, case_file, action_file):
		case_browsers = suite_browsers.split(",")
		case_hubs = suite_hubs.split(",")
		case_targets = suite_targets.split(",")
		for case_browser in case_browsers:
			for case_hub in case_hubs:
				for case_target in case_targets:
					with open(case_file, 'rt') as cases:
						for case in cases:
							case = case.strip()
							case_fields = case.split("  ")
							case_identifier, case_description, explicit_wait, case_actions = case_fields
							if case_identifier == suite_case:
								Jam.run_test(case_identifier, case_description, explicit_wait, case_actions, case_browser, case_hub, case_target, suite_screenshot, action_file)
	
	def run_test(case_identifier, case_description, explicit_wait, case_actions, case_browser, case_hub, case_target, action_screenshot, action_file):
		engage_driver = Nexus.engage_driver(case_browser, case_hub, case_target)
		print("   Test Case: " + case_identifier)
		journey_actions = case_actions.split(",")
		for count, journey_action in enumerate(journey_actions, start=1):
			print("      Step " + str(count) + ":")
			with open(action_file, 'rt') as actions:
				for action in actions:
					action = action.strip()
					action_fields = action.split("  ")
					action_identifier, action_type, action_on, action_by, action_text, action_pause, action_description = action_fields
					if journey_action == action_identifier:
						print("      --> Action: " + action_description)
						Nexus.execute_test(engage_driver, case_hub, explicit_wait, action_identifier, action_type, action_on, action_by, action_text, action_screenshot, action_pause)
		Nexus.release_driver(engage_driver)

start_time = time.time()
Jam.execute_suite('cases', 'actions')
elapsed_time = (time.time() - start_time) / 60
print("\n   Duration: " + str(elapsed_time))
