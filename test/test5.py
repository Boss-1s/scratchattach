from typing import get_type_hints
import time
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from key_multivalue_storage import Storage as s

sload = s.Load
sdelete = s.Delete
sedit = s.Edit

db_add_subval("test.json", "test_top_level_key", "sk1", "val1", "sk2", "skibidi toilet")
db_add_subval("test.json", "test_top_level_key2", "sk1", "val1", "sk2", "the fate of sigma")
db_add_subval("test.json", "test_top_level_key2", "sk3", "val3", "sk4", "the fate of shard")
time.sleep(2)
db_set_val("test.json", "test_top_level_key", "sk2", "sigma")
time.sleep(2)
print(db_get_keys("test.json"))
time.sleep(1)
print(db_get_subkeys_values("test.json", "test_top_level_key"))
time.sleep(1)
db_delete_key("test.json", "test_top_level_key2")
time.sleep(1)
db_delete_all("test.json")

print("test passed sucessfully")
