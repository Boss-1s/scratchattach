import time,sys,os,json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from key_multivalue_storage import Storage as s

file = "otest.json"

def db_add_subval(db, key, subkey, val, subkey2=None, val2=None, subkey3=None, val3=None, subkey4=None, val4=None, subkey5=None, val5=None):
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
    
    try:s(key, **skwargs).store(db)
    except Exception as e:print(f"Process failed: {e}")
    print(f"Sucessfully added values {list(skwargs.values())} to subkeys {list(skwargs.keys())}, respectively.")

def db_set_val(db, key, subkey, val):
    try:s.Edit.propval(db, key, subkey, val)
    except Exception as e:print(f"Process failed: {e}")
    print(f"Sucessfully set subkey {subkey} to value {val}.")

def db_get_keys(db):return s.Load.keys(db)

def db_get_subkeys_values(db, top_lv_key, keys=True, raw=False):
    return s.Load.values(db, top_lv_key, keys=keys, raw=raw)
    
def db_delete_key(db, key):
    try:s.Delete.by_key(db, key)
    except Exception as e:print(f"Process failed: {e}")
    print(f"Sucessfully deleted key {key} and all its child data.")

def db_delete_all(db):
    try:s.Delete.all(db, warn=False)
    except Exception as e:print(f"Process failed: {e}")
    print(f"Sucessfully deleted all data from {db}.")

time.sleep(2)
db_delete_all(file)

print("Begin test\n"+("-"*20)+"\nPart 1: Storing, Editing, and Deleting via JSON\n"+("-"*20))

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
assert db_get_subkeys_values(file, "test_top_level_key2") == ["sk3: val3","sk4: the fate of shard"],"Adding subkey-value pairs has failed. Try checking the store method."
assert db_get_subkeys_values(file, "test_top_level_key2", keys=False) == ["val3","the fate of shard"],"Adding subkey-value pairs has failed. Try checking both the store and db_add_subval methods."
db_set_val(file, "test_top_level_key", "sk2", "sigma")
assert db_get_subkeys_values(file, "test_top_level_key") == ["sk1: val1","sk2: sigma",],"Editing subkey-value pairs has failed. Try checking the Edit.propval method."
db_delete_key(file, "test_top_level_key2")
assert db_get_keys(file) == ["test_top_level_key"], "Deleting a key has failed. Check the Delete.by_key method."
db_delete_all(file)
assert db_get_keys(file) == [], "Bulk deleting has failed. Check the Delete.all method."
print("Part 1 passed.")

print(("-"*20)+"\nPart 2: Storing, Editing, and Deleting via dunder methods\n"+("-"*20))

s1 = s("test1", sk1="val1", sk2="val2")
s2 = s("test1", sk4="val1", sk6="val2", sk3="val3")
s3 = s("test2", sk4="val1", sk6="val2", sk3="val3")

print("Part 2.1: Comparisons")

assert s1 != s2 # if this fails, python probably updated without notice lol
assert repr(s1) == "Storage(top_lv_key=test1, key_value_pairs=[sk1='val1', sk2='val2'])", "The repr representation of instance s1 is incorrect. Check the __repr__ method."
assert repr(s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk4='val1', sk6='val2', sk3='val3'])", "The repr representation of instance s1 is incorrect. Check the __repr__ method."
assert repr(s3) == "Storage(top_lv_key=test2, key_value_pairs=[sk4='val1', sk6='val2', sk3='val3'])", "The repr representation of instance s1 is incorrect. Check the __repr__ method."
# assert str(s1) == "(str repr)" # find a way to assert the string representation
assert s1<s2
try:assert s2>s3
except ValueError:pass
else:raise AssertionError("Key comparison most likely failed, otherwise an unknown error occurred. Check the __lt__ method.")
  
print("Part 2.1 passed.\n-----\nPart 2.2: Arithmetic")

assert repr(s1+
            {"sk7": "67",
             "sk8": "hehe"
            }+s2
           )=="Storage(top_lv_key=test1, key_value_pairs=[sk1='val1', sk2='val2', sk7='67', sk8='hehe', sk4='val1', sk6='val2', sk3='val3'])", "Adding a dict to the instance has failed. Check the __add__ and __radd__ methods."
s1 = s("test1", sk1="val1", sk2="val2")
assert repr(s1+s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk1='val1', sk2='val2', sk4='val1', sk6='val2', sk3='val3'])", "Adding two instances has failed. Check the __add__ and __radd__ methods."
s1 = s("test1", sk1="val1", sk2="val2")
assert repr(s1+["val1", "val2"]) == "Storage(top_lv_key=test1, key_value_pairs=[sk1='val1', sk2='val2', undefined=['val1', 'val2']])"
s1 = s("test1", sk1="val1", sk2="val2")
assert repr(s1-s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk1='val1', sk2='val2'])"
try:assert s3-s2
except ValueError:pass
else:raise AssertionError("Key comparison most likely failed, otherwise an unknown error occurred. Check the __sub__ and __rsub__ methods.")
assert s2-s1 == s2/s1, "Division did not switch to subtraction. Check the __sub__, __rsub__, __truediv__, and __rtruediv__."
assert str(s1/2) == "[Storage(top_lv_key=test1, key_value_pairs=[sk1='val1']), Storage(top_lv_key=test1, key_value_pairs=[sk2='val2'])]", "Division has failed. Check the __truediv__ method."
assert s1/1 == [s1], "Division has failed. Check the __truediv__ method."
try:assert 1/s1
except TypeError:pass
else:raise AssertionError("Division has failed. Check the __truediv__ and __rturediv__ methods.")
  
print("Part 2.2 passed.\n-----\nPart 2.3: Bitwise Operators")

s2 = s("test1", sk4="val1", sk6="val2", sk3="val3")
s3 = s("test1", sk4="val1", sk6="val2", sk3="val3")

assert repr(s3&s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk6='val2', sk4='val1'])", "The bitwise operator AND (&) has failed. Check the __and__ method."
assert repr(s3|s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk6='val2', sk4='val1', sk5='val3', sk3='val3'])", "The bitwise operator OR (|) has failed. Check the __or__ method."
assert repr(s3^s2) == "Storage(top_lv_key=test1, key_value_pairs=[sk5='val3', sk3='val3'])", "The bitwise operator XOR (^) has failed. Check the __xor__ method."
assert repr(s3<<1) == "Storage(top_lv_key=test1, key_value_pairs=[sk6='val2', sk3='val3'])", "The bitwise operator LEFT_SHIFT (<<) has failed. Check the __lshift__ method."
assert repr(s3>>2) == "Storage(top_lv_key=test1, key_value_pairs=[sk4='val1'])", "The bitwise operator RIGHT_SHIFT (>>) has failed. Check the __rshift__ method."

print("Part 2.3 passed.\n-----\nPart 2.4: Indexing and Slicing")

print("\nTest passed sucessfully")
