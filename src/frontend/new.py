# import os
# save_dir = os.path.join(os.path.dirname(__file__), '..', 'travel_plans')

# save_dir_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'travel_plans'))

# # print(os.path.dirname(__file__))
# save_dir_2 = os.path.dirname(os.path.dirname(__file__))
# save_dir_3 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "travel_plans")

# BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) 
# USER_FILE = os.path.join(BASE_DIR, "data", "users.json")


# # print(save_dir)
# # print(save_dir_1)
# # print(save_dir_2)
# # print(save_dir_3)

# print(BASE_DIR)
# print(USER_FILE)

import datetime
current_date = datetime.datetime.now().strftime("%Y-%m-%d")
print(current_date)

import os
print(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "outputs","travel_plans"))

