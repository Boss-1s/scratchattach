import time,sys,os,json
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from key_multivalue_storage import Storage as s

file = "otest.json"

#@client.request(response_priority=2)
def db_add_subval(db, key, subkey, val, subkey2=None, val2=None, subkey3=None, val3=None, subkey4=None, val4=None, subkey5=None, val5=None):
    #max 5 subkey-value pairs at the same time
    skwargs = {}
    skwargs.update({subkey: val})
    if subkey2 is not None and val2 is not None:
        skwargs.update({subkey2: val2})
    if subkey3 is not None and val3 is not None:
        skwargs.update({subkey3: val3})
    if subkey4 is not None and val4 is not None:
        skwargs.update({subkey4: val4})
    if subkey5 is not None and val5 is not None:
        skwargs.update({subkey5: val5})
    
    try:
        s(key, **skwargs).store(db)
    except Exception as e:
        print(f"Process failed: {e}")
        #return f"unknown error occured: {e}"
    print(f"Sucessfully added values {list(skwargs.values())} to subkeys {list(skwargs.keys())}, respectively.")
    #return "Success"

#@client.request(response_priority=2)
def db_set_val(db, key, subkey, val):
    try:
        s.Edit.propval(db, key, subkey, val)
    except Exception as e:
        print(f"Process failed: {e}")
        #return f"unknown error occured: {e}"
    print(f"Sucessfully set subkey {subkey} to value {val}.")
    #return "Success"

#@client.request(response_priority=3)
def db_get_keys(db):
    return s.Load.keys(db)

#@client.request(response_priority=3)
def db_get_subkeys_values(db, top_lv_key, keys=True, raw=False):
    return s.Load.values(db, top_lv_key, keys=keys, raw=raw)
    
#@client.request(response_priority=2)    
def db_delete_key(db, key):
    try:
        s.Delete.by_key(db, key)
    except Exception as e:
        print(f"Process failed: {e}")
        #return f"unknown error occured: {e}"
    print(f"Sucessfully deleted key {key} and all its child data.")
    #return "Success"

#@client.request(response_priority=2)
def db_delete_all(db):
    try:
        s.Delete.all(db, warn=False)
    except Exception as e:
        print(f"Process failed: {e}")
        #return f"unknown error occured: {e}"
    print(f"Sucessfully deleted all data from {db}.")
    #return "Success"

db_add_subval(file, "test_top_level_key", "sk1", "val1", "sk2", "skibidi toilet")
assert db_get_keys(file) == ["test_top_level_key"], "Adding a top level key has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key") == ["sk1: val1","sk2: skibidi toilet"],"Adding subkey-value pairs has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key", keys=False) == ["val1","skibidi toilet"],"Adding subkey-value pairs has failed. Try checking both the store and db_add_subval methods."
db_add_subval(file, "test_top_level_key2", "sk1", "val1", "sk2", "the fate of sigma")
assert db_get_keys(file) == ["test_top_level_key","test_top_level_key2"], "Adding a top level key has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key2") == ["sk1: val1","sk2: the fate of sigma"],"Adding subkey-value pairs has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key2", keys=False) == ["val1","the fate of sigma"],"Adding subkey-value pairs has failed. Try checking both the store and db_add_subval methods."
db_add_subval(file, "test_top_level_key2", "sk3", "val3", "sk4", "the fate of shard")
assert db_get_keys(file) == ["test_top_level_key", "test_top_level_key2"], "Adding a top level key has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key2") == ["sk1: val1","sk2: the fate of sigma","sk3: val3","sk4: the fate of shard"],"Adding subkey-value pairs has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key2", keys=False) == ["val1","the fate of sigma","val3","the fate of shard"],"Adding subkey-value pairs has failed. Try checking both the store and db_add_subval methods."
db_set_val(file, "test_top_level_key", "sk2", "sigma")
assert db_get_subkeys_values(file, "test_top_level_key") == ["sk1: val1","sk2: sigma",],"Editing subkey-value pairs has failed. Try checking the Edit.propval method."
db_delete_key(file, "test_top_level_key2")
assert db_get_keys(file) == ["test_top_level_key"], "Deleting a key has failed. Check the Delete.by_key method."
db_delete_all(file)
assert db_get_keys(file) == [], "Bulk deleting has failed. Check the Delete.all method."
print("\ntest passed sucessfully")
