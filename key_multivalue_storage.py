from __future__ import annotations
import os,json,uuid,warnings,logging,difflib,datetime,builtins
from typing import Any, Optional, Self, Generator
from functools import total_ordering
from datetime import datetime

__all__ = ["Storage", "Storage.Delete", "Storage.Load", "Storage.Edit", "Delete", "Load", "Edit"]
logger: logging.Logger | None = None

def _set_up_logger(dir: str, 
				   fname: str, 
				   lname: str, 
				   format: str = "%(levelname)s:%(name)s:%(message)s",
				  ) -> None:
	# Set up logging
	os.makedirs(dir, exist_ok=True)
	with open(dir+fname, 'w'):pass
	logger = logging.getLogger(lname)
	logger.setLevel(logging.INFO)
	logger.propagate = False
	logger.addHandler(logging.FileHandler(dir+fname).setFormatter(logging.Formatter(format)))

def _toggle_logger(self) -> None:
	"""Toggles the logger on and off."""
	if logger.level == logging.CRITICAL + 100:logger.setLevel(logging.INFO)
	else:logger.setLevel(logging.CRITICAL + 100)

def print(*args, **kwargs) -> None:
	builtins.print("[key_multivalue_storage.py] ", *args, **kwargs)

class _KeyNotFoundError(KeyError):
	"""Custom exception raised when a key is not found."""
	def __init__(self, file: str, mkey: str | uuid.UUID, message="") -> None:
		self.mkey = mkey
		self.file = file
		self.message = f"The following key was not found in {file}: {mkey}" if message == "" else message
		super().__init__(self.message)

@total_ordering
class Storage:
	"""
	Class for monokey-multivalue storage.
	Developed for the project ScratchChat by Boss_1s -> https://scratch.mit.edu/projects/1051418168
	Used in conjuction with scratchattach.
	
	Usage:
	Storage(key: str, kwargs1: Any, kwargs2: Any...) -> Create an instance of the Storage class to store
	|
	| Storage.store(file_path: str, instant_delete: bool, indent: int) -> Stores created instance into a JSON file
	|
	| Storage.DeleteWarning(UserWarning) -> a custom warning class used to warn about deleteing in Storage.Delete.all().
	|
	| Storage.Load
	|  --> Storage.Load.by_key(file_path: str, key: str|uuid.UUID, raw: bool) -> load a key and its values.
	|  --> Storage.Load.by_index(file_path: str, index: int, raw: bool) -> same as above, but load by index, not key.
	|  --> Storage.Load.keys(file_path: str) -> returns the key of a file only.
	|  --> Storage.Load.values(file_path: str, key: str|uuid.UUID, keys: bool, raw: bool) -> returns the values of a key. Can return keys if keys=True
	|
	| Storage.Edit
	|  --> Storage.Edit.propkey(file_path: str, top_lv_key: str | uuid.UUID, oldpropkey: str, newpropkey: str) -> Edits the name of a subkey within a key within a JSON file.
	|  --> Storage.Edit.propval(file_path: str, top_lv_key: str | uuid.UUID, propkey: str, newval: str) -> Edits the value of a subkey within a key within a JSON file.
	|  --> Storage.Edit.key(file_path: str, oldkey: str | uuid.UUID, newkey: str | uuid.UUID)
	| 
	| Storage.Delete
	|  --> Storage.Delete.by_propkey(file_path: str, top_level_key: str | uuid.UUID, property_key: str) -> deletes a subkey-value pair within a key
	|  --> Storage.Delete.by_key(file_path: str, key: str | uuid.UUID) -> Deletes a key-multivalue pair and its values
	|  --> Storage.Delete.all(file_path: str, warn: bool) -> Deletes all of a JSON Storage file.
	|
	| (Dunder methods)
	"""

	global logger
	
	#Define public and private methods/classes
	__all__ = ["store", "DeleteWarning", "Load", "Edit", "Delete", "__str__"]
	
	def __init__(self, key: str | uuid.UUID, **kwargs: Any) -> None:
		"""initiate instance paramaters"""
		# Setup logger first...
		self.instance_id = uuid.uuid4() #uuid7.uuid7() for support with CPython >=3.12
		# ...then attempt to set values
		self.key = str(key) if isinstance(key, uuid.UUID) else key
		self.values = kwargs
	
	@staticmethod
	def _encode(string: Any) -> int:
		"""Encodes a value using a simple character-matching system, simmilar to a one-time pad but reusable."""
	
		if not isinstance(string, str):
			string = str(string)
	
		char="""`1234657809=-\\][p';/.,lokimnjuyhbtfcvgrs edxzawq~+_)(*&^T$%@!#REDFGSWAQZXVCBNHYUJMKI<>LOP:{}|"?><"""
		i=0
		output=''
		while i < len(string):
			currentchar=string[i]
			i2: int=0
			i3=''
			while not i3 == currentchar:
				i3=char[i2]
				i2=i2+1
				if i3 == currentchar:
					break
			i2=f"{i2}"
			output=f"{output}{len(i2)}{i2}"
			i=i+1
		return int(output)
	
	@staticmethod
	def _decode(string: str | int) -> str:
		"""Decodes a value encoded with Storage._encode"""
		
		if not isinstance(string, (str, int)): # Accept encoded int or its string repr
			raise TypeError("Expected encoded string or integer for decoding.")
	
		to_decode=str(string)
		
		char="""`1234657809=-\\][p';/.,lokimnjuyhbtfcvgrs edxzawq~+_)(*&^T$%@!#REDFGSWAQZXVCBNHYUJMKI<>LOP:{}|"?><"""
		i=0
		output=''
		while i < len(to_decode):
			totalchars=int(to_decode[i])
			print(f"_decode: DEBUG: totalchars {totalchars}") 
			currentchar=int(to_decode[i+1:i+1+totalchars])
			print(f"_decode: DEBUG: currentchar={currentchar}") 
			#Bounds Check
			if not (0 <= currentchar-1 < len(char)):
				raise ValueError(f"Decoding error: Index {currentchar - 1} out of bounds for character map.")
			output=f"{output}{char[currentchar-1]}"
			i=i+1+totalchars
		return output
	
	def _to_dict(self) -> dict[str, dict[str, Any]]:
		"""Converts key-multivalue pair into a dict for json dumping"""
		encoded_values: dict[str, Any] = {}
		for prop_key, prop_value in self.values.items():
			encoded_values[prop_key] = self._encode(prop_value) # Use self._encode
		
		return {
			self.key: encoded_values
		}

	@classmethod
	def _from_dict(cls, data_dict: dict[str, dict[str, Any]], raw: bool=False) -> Storage:
		"""Extracts data from a dict into seperate key-multivalue pairs, decoding values in the process."""

		print(f"_from_dict: DEBUG: data_dict={data_dict}")
		print(f"_from_dict: DEBUG: data_dict={raw}")
		
		if not isinstance(data_dict, dict) or len(data_dict) != 1:
			raise ValueError("Expected a dictionary with a single top-level key.")
		
		top_level_key: str = list(data_dict.keys())[0]
		og_nested_values: dict[str, Any] = data_dict[top_level_key]
		
		if not isinstance(og_nested_values, dict):
			raise ValueError("Expected nested values to be a dictionary.")
	
		if not raw:
		  decoded_values: dict[str, Any] = {}
		  # Decide which values to decode.
		  # Only decode if the value is an int (encoded string) or a string that looks like an encoded int.
		  for prop_key, encoded_value in og_nested_values.items():
			  if isinstance(encoded_value, int) or (isinstance(encoded_value, str) and encoded_value.isdigit()):
				  try:
					  og_nested_values[prop_key] = cls._decode(string=encoded_value)
				  except ValueError: # Handle cases where decoding fails, keep original or raise error
					  og_nested_values[prop_key] = encoded_value # Keep as is if decoding fails
			  else:
				  og_nested_values[prop_key] = encoded_value # Keep non-encoded values as is
		
		return cls(top_level_key, **og_nested_values)
	
	@staticmethod
	def __store(file_path: str, dict_to_dump: dict[str, dict[str, Any]], indent: int=4) -> None:
		"""For private use by delete class, works just like Storage.store() but dict is already created, so no instance is required."""
		"""Store a key-multivalue pair into a json file."""
		all_data: dict[str, dict[str, Any]] = {}
		try:
			with open(file_path, "r") as f:
				all_data = json.load(f)
		except FileNotFoundError:
			warnings.warn(f"__store: WARNING: File '{file_path}' not found. Creating a new one.")
		except json.JSONDecodeError:
			warnings.warn(f"__store: WARNING: File '{file_path}' contains invalid JSON. Overwriting.", SyntaxWarning)
			all_data = {}
	
		all_data.update(dict_to_dump)
	
		try:
			with open(file_path, "w") as f:
				json.dump(all_data, f, indent=indent)
			print(f"__store: INFO: Data for key '{list(dict_to_dump.keys())[0]}' stored successfully in '{file_path}'.")
		except IOError as e:
			print(f"__store: ERROR: Error writing to file '{file_path}': {e}")
	
	@staticmethod
	def __is_warning_category_ignored(category: Any) -> bool:
		for action, _, cat, _, _ in warnings.filters:
			if action == 'ignore' and category==cat:
				return True
		return False
		
	def store(self, file_path: str, instant_delete: bool=False, indent: int=4) -> None:
		"""Store a key-multivalue pair into a json file."""
		all_data: dict[str, dict[str, Any]] = {}
		try:
			with open(file_path, "r") as f:
				all_data = json.load(f)
		except FileNotFoundError:
			warnings.warn(f"store: WARNING: File '{file_path}' not found. Creating a new one.") 
		except json.JSONDecodeError:
			warnings.warn(f"store: WARNING: Warning: File '{file_path}' contains invalid JSON. Overwriting.", SyntaxWarning)
			all_data = {}
		
		if ".json" not in file_path:
			fp = str(file_path) + ".json"
		
		all_data.update(self._to_dict())
	
		try:
			with open(file_path, "w") as f:
				json.dump(all_data, f, indent=indent)
			print(f"store: INFO: Data for key '{self.key}' stored successfully in '{file_path}'.") 
		except IOError as e:
			print(f"store: ERROR: Error writing to file '{file_path}': {e}") 

		if instant_delete:del self

	class DeleteWarning(UserWarning):
		"""Custom warning when attempting to delete the contents of a whole database."""
		def __init__(self, message: str=None, method: str=None) -> None:
			super().__init__(message)
			self.method = method

		def __str__(self) -> str:
			return(f"{self.method}: WARNING: DeleteWarning: {self.args[0]}")
		
	class AdditionFailureWarning(RuntimeWarning):
		"""Custom warning when attempting to add a Storage instance with a dictionary or list."""
		def __init__(self, message: str=None, method: str=None) -> None:
			super().__init__(message)
			self.method = method

		def __str__(self) -> str:
			return(f"{self.method}: WARNING: AdditionFailureWarning: {self.args[0]}")
			
	class SubtractionFailureWarning(RuntimeWarning):
		"""
		Custom warning when attempting to subtract a Storage instance by a dictionary, and vice versa.
		Also applies to division, despite the name.
		"""
		def __init__(self, message: str=None, method: str=None) -> None:
			super().__init__(message)
			self.method = method

		def __str__(self) -> str:
			return(f"{self.method}: WARNING: SubtractionFailureWarning: {self.args[0]}")
			
	class Load:
		__all__ = ["by_key", "by_index", "keys", "values"]
	  
		@classmethod
		def by_key(cls, file_path: str, key: str | uuid.UUID, raw: bool=False) -> Optional['Storage']:
			"""Load a json file and find the key to extract a single key-multivalue pair and its values"""
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Load.by_key: ERROR: Failed to load with key '{key}' - file '{file_path}' does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Load.by_key: ERROR: Failed to load with key '{key}' - file '{file_path}' contains invalid JSON.")
				return None
	
			#Debug
			print(f"Load.by_key: DEBUG: Data loaded from '{file_path}': {loaded_data}")
			print(f"Load.by_key: DEBUG: Keys in loaded_data: {loaded_data.keys()}")
			print(f"Load.by_key: DEBUG: Type of loaded_data keys: {[type(k) for k in loaded_data.keys()]}")
			print(f"Load.by_key: DEBUG: Key being searched for: '{key}'")
			print(f"Load.by_key: DEBUG: Type of search key: {type(key)}")
		  
			# Super-detailed comparison check
			found_in_keys = False
			for k in loaded_data.keys():
				print(f"Load.by_key: DEBUG: Comparing '{key}' (len={len(key)},"+
					  f" repr={repr(key)}) with loaded key '{k}' (len={len(k)}, repr={repr(k)})")
				if key == k:
					found_in_keys = True
					print(f"Load.by_key: DEBUG: Match found for key '{key}'!")
					break
			
			if key in loaded_data and found_in_keys: #Use the flag from the detailed comparison
				try:
					return Storage._from_dict({key: loaded_data[key]}, raw) 
				except ValueError as e:
					print(f"Load.by_key: ERROR: Error reconstructing object for key '{key}': {e}")
					return None
			else:
				print("Load.by_key: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, key)
	
		@classmethod
		def by_index(cls, file_path: str, index: int, raw: bool=False) -> Optional['Storage']:
			"""Load a json file and find the index at which to extract a single key-multivalue pair and its values."""
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Failed to load by index '{index}' - file '{file_path}' does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Failed to load by index '{index}' - file '{file_path}' contains invalid JSON.")
				return None
	
			keys = list(loaded_data.keys())
	
			# Check if the provided index is valid
			if not (0 <= index < len(keys)):
				logger.warning(f"Index '{index}' is out of bounds for the keys in '{file_path}'. Available keys: {len(keys)}")
				return None
	
			target_key: str = keys[index]
			if target_key in loaded_data:
				try:
					return Storage._from_dict({target_key: loaded_data[target_key]}, raw) 
				except ValueError as e:
					print(f"Error reconstructing object for key '{target_key}' at index '{index}': {e}")
					return None
			else:
				print("Load.by_index: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, 
										target_key, 
										f"Key '{target_key}' unexpectedly not found"+
										f" in loaded data for index '{index}'.")
	
		@classmethod
		def keys(cls, file_path: str) -> Optional[list[str]]:
			"""Load a json file and returns the keys of that file."""
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Load.keys: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Load.keys: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			return list(loaded_data.keys())
	
		@classmethod
		def values(cls, file_path: str, key: str | uuid.UUID, keys: bool=False, raw: bool=True) -> Optional[list[str]]:
			"""
			Loads a json file and returns the values under the inputed key. Unlike other loading methods, this one returns the raw values by default.
			Keys can also be returned as a key-value pair if keys=True.
			"""
			print(f"Load.values: DEBUG: file_path={file_path}")
			print(f"Load.values: DEBUG: key={key}")
			print(f"Load.values: DEBUG: keys={keys}")
			print(f"Load.values: DEBUG: raw={raw}")
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Load.values: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Load.values: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None

			print(f"Load.values: DEBUG: loaded_data={loaded_data}")
			print(f"Load.values: DEBUG: key in loaded_data? {key in loaded_data}")

			print(f"Load.values: DEBUG: dict_to_load={({key: loaded_data[key]})}")
			if key in loaded_data:
				try:
				   subsection: dict[str, dict[str, Any]] = Storage._from_dict({key: loaded_data[key]}, raw) 
				except ValueError as e:
					print(f"Load.values: ERROR: Error reconstructing object for key '{key}': {e}")
					return None
			else:
				print("Load.values: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, key)
	
			items: list[str] = []
			for key, val in subsection.values.items():
				if keys:
					items.append(f"{key}: {val}")
					print(f"Load.values: DEBUG: items.append(f'{key}: {val}')")
				else:
					items.append(val)
					print(f"Load.values: DEBUG: items.append({val})")
			return items
	
	class Edit:
		__all__ = ["propkey", "propval", "key"]
	
		@classmethod
		def propkey(cls, 
					file_path: str, 
					top_lv_key: str | uuid.UUID, 
					oldpropkey: str, 
					newpropkey: str,
					new: bool=True, #deprecated
					noexist_ok: bool=True) -> None:
			"""Edits the name of subkey within a key within a JSON file. The value of that subkey does not change."""
			warnings.warn("WARNING! The 'new' argument is no longer used. If you still use new=True or new=False, "+
						  "please use noexist_ok=True or noexist_ok=False.", DeprecationWarning)
			noexist_ok = new if new else noexist_ok
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Edit.propkey: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Edit.propkey: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			if top_lv_key in loaded_data:
				try:
				   subsection: dict[str, dict[str, Any]] = Storage._from_dict({top_lv_key: loaded_data[top_lv_key]}) 
				except ValueError as e:
					print(f"Edit.propkey: ERROR: Error reconstructing object for key '{top_level_key}': {e}")
					return None
			else:
				print("Edit.propkey: ERROR: Encountering _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, top_lv_key)
	
			items: dict[str, Any] = {}
			if oldpropkey in subsection:
				for propkey, propval in subsection.values.items():
					if propkey == oldpropkey:items[newpropkey] = propval
					else:items[propkey] = propval
			elif noexist_ok:
				warnings.warn(f"Subkey {oldpropkey} was not found. Creating a new subkey under the name"+
					  		  f" {newpropkey} with value '' (override this with noexist_ok=False, will raise exception)")
				for propkey, propval in subsection.values.items():items[propkey] = propval
				items[newpropkey] = ''
			else:
				print("Edit.propkey: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, oldpropkey)
	
			to_dump: dict[str, dict[str, Any]] = {
				top_lv_key: items
			}
	
			Storage._Storage__store(file_path, to_dump)
			print(f"Edit.propkey: INFO: Sucessfully renamed {oldpropkey} to {newpropkey}.")
	
		@classmethod
		def propval(cls, file_path: str, top_lv_key: str | uuid.UUID, propkey: str, newval: str) -> None:
			"""Edits the value of a subkey within a key within a JSON file. The subkey of that value does not change."""
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Edit.propval: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Edit.propval: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			if top_lv_key in loaded_data:
				try:
				   subsection: dict[str, dict[str, Any]] = Storage._from_dict({top_lv_key: loaded_data[top_lv_key]}) 
				except ValueError as e:
					print(f"Edit.propval: ERROR: Error reconstructing object for key '{top_lv_key}': {e}")
					return None
			else:
				print("Edit.propval: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, top_lv_key)
	
			items: dict[str, Any] = {}
			for propkey1, propval in subsection.values.items():
				if propkey == propkey1:
					oldval = propval
					items[propkey] = newval
				else:
					items[propkey1] = propval
	
			to_dump: dict[str, dict[str, Any]] = {top_lv_key: items}
	
			Storage._Storage__store(file_path, to_dump)
			print(f"Edit.propval: INFO: Sucessfully changed value {oldval} "+
				  f"to {newval} under key {top_lv_key}.{propkey}.")
	
		@classmethod
		def key(cls, file_path: str, oldkey: str | uuid.UUID, newkey: str | uuid.UUID) -> None:
			"""
			Deletes a key-multivalue pair and its values within a JSON file. 
			Does NOT create a new instance of Storage, you will have to regrab
			the values to see the changes.
			"""
			try:
				with open(file_path, "r") as f:loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Edit.key: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Edit.key: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			print(f"Edit.key: DEBUG: loaded_data.keys()={loaded_data.keys()}")
			print(f"Edit.key: DEBUG: loaded_data.values()={loaded_data.values()}")
			print(f"Edit.key: DEBUG: loaded_data={loaded_data}")
	
			if oldkey in loaded_data:
				loaded_data = {
					newkey if key == oldkey else key: value
					for key, value in loaded_data.items()
				}
				print(f"Edit.key: DEBUG: New dictionary: loaded_data={loaded_data}")
				try:
					with open(file_path, "w") as f:
						json.dump(loaded_data, f)
						print(f"Successfully changed key '{oldkey}' to '{newkey}'.")
				except IOError as e:
					print(f"Error writing to file '{file_path}' after deletion: {e}")
			else:
				print("Edit.key: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, oldkey)
	
	class Delete:
		__all__ = ["by_propkey", "by_key", "all"]
	  
		@classmethod
		def by_propkey(cls, file_path: str, top_level_key: str | uuid.UUID, property_key: str) -> None:
			"""
			Deletes a property within a top-level key in the JSON file. 
			Does NOT create a new instance of Storage, you will have to 
			regrab the values to see the changes.
			"""
			try:
				with open(file_path, "r") as f:loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Delete.by_propkey: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Delete.by_propkey: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
			
			if top_level_key in loaded_data:
				try:subsection: dict[str, dict[str, Any]] = Storage._from_dict({top_level_key: loaded_data[top_level_key]}) 
				except ValueError as e:
					print(f"Delete.by_propkey: ERROR: Error reconstructing object for key '{top_level_key}': {e}")
					return None
			else:
				print("Delete.by_propkey: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, top_level_key)
			
			items: dict[str, Any] = {}

			for propkey, propval in subsection.values.items():
				if propkey != property_key:
					items[propkey] = propval
	
			print(f"Delete.by_propkey: DEBUG: items={items}, type={type(items)}")
			print(f"Delete.by_propkey: DEBUG: subsection={subsection}")
			print(f"Delete.by_propkey: DEBUG: top_level_key={top_level_key}, type=({type(top_level_key)})")
		  
			to_dump: dict[str, dict[str, Any]] = {top_level_key: items}
	
			print(f"Delete.by_propkey: DEBUG: to_dump={to_dump}")
	
			Storage._Storage__store(file_path, to_dump)
			print(f"Delete.by_propkey: INFO: Sucessfully deleted subkey {property_key} and its value.")
	
		@classmethod
		def by_key(cls, file_path: str, key: str | uuid.UUID) -> None:
			"""
			Deletes a key-multivalue pair and its values within a JSON file. 
			Does NOT create a new instance of Storage, you will have to regrab the 
			values to see the changes.
			"""
			try:
				with open(file_path, "r") as f:
					loaded_data: dict[str, dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				print(f"Delete.by_key: ERROR: Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				print(f"Delete.by_key: ERROR: Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			print(f"Delete.by_key: DEBUG: loaded_data.keys()={loaded_data.keys()}")
			print(f"Delete.by_key: DEBUG: loaded_data.values()={loaded_data.values()}")
			print(f"Delete.by_key: DEBUG: loaded_data={loaded_data}")
	
			if key in loaded_data:
				del loaded_data[key]
				try:
					with open(file_path, "w") as f:
						json.dump(loaded_data, f)
						print(f"Delete.by_key: INFO: Successfully deleted key '{key}' from '{file_path}'.")
				except IOError as e:
					print(f"Delete.by_key: ERROR: Error writing to file '{file_path}' after deletion: {e}")
			else:
				print("Delete.by_key: ERROR: Encountered _KeyNotFoundError")
				raise _KeyNotFoundError(file_path, key)
	
			
		@staticmethod
		def all(file_path: str, warn: bool=True) -> None:
			if Storage._Storage__is_warning_category_ignored("DeleteWarning") or warn:
				warnings.warn(Storage.DeleteWarning(
					f"You are about to delete ALL of the data inside the file {file_path}. "+ 
				    "This is an irreversible action! If you are COMPLETELY CERTAIN about deleting all the data, "+
				    "add Storage.Delete.all(file_path, warn=False) to your script. If you never want to see this warning"+
				    " again, add warnings.filterwarning(category=Storage.DeleteWarning) to your script.",method="Delete.all"))
			else:
				with open(file_path, "w") as f:
					json.dump({}, f)
					print(f"Delete.all: INFO: Deleted all data from {file_path} sucessfully.")
					return None

	# --- #
	
	def __str__(self) -> str:
		"""Defines how the object should be represented in a easy-to-read, user-friendly form."""
		values_str: str = ',\n'.join([f"    {prop}: {repr(value)}" for prop, value in self.values.items()])
		return "{\n" + f"  {self.key}: {{\n{values_str}\n  }}\n" + "}"

	def __repr__(self) -> str:
		"""Defines how the object should be represented in an unambiguous, dev-friendly form."""
		values_str: str = ', '.join([f"{prop}={repr(value)}" for prop, value in self.values.items()])
		return f"Storage(top_lv_key={self.key}, key_value_pairs=[{values_str}])"

	def __eq__(self, other) -> bool:
		"""Defines how the object should be compared as equal."""
		if isinstance(other, type(self)):
			if self.key==other.key and self.values.items()==other.values.items():
				return True
			return False
		return NotImplemented

	def __lt__(self, other) -> bool:
		"""Defines how the object should be compared as less than."""
		if isinstance(other, type(self)):
			if self.key!=other.key:raise ValueError("Both instances must have the same top level key")
			if len(self.values.items()) < len(other.values.items()):
				return True
			return False
		return NotImplemented

	def __le__(self, other) -> bool:
		"""Defines how the object should be compared as less than or equal to."""
		if isinstance(other, type(self)):
			if len(self.values.items()) < len(other.values.items()) or self==other:
				return True
			return False
		return NotImplemented

	def __add__(self, other: Storage | dict[str, Any] | list[Any]) -> Self:
		"""Defines how to add two objects, same type or no."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				self.values.update(other.values)
				return Storage(self.key, **self.values)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			warnings.warn(self.AdditionFailureWarning("WARNING! You are strongly advised against adding a Storage "+
						  "instance and a dict/list together, as it may break the Storage "+
						  "instance that is created.",method="__add__"))
			self.values.update(other)
			return Storage(self.key, **self.values)
		elif isinstance(other, list):
			warnings.warn(self.AdditionFailureWarning("WARNING! You are strongly advised against adding a Storage "+
						  "instance and a dict/list together, as it may break the Storage "+
						  "instance that is created.",method="__add__"))
			self.values.update({"undefined": other})
			return Storage(self.key, **self.values)
		else:return NotImplemented
	
	def __radd__(self, other: Storage | dict[str, Any]) -> Self:
		"""Defines how to add two objects, same type or no."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				self.values.update(other.values)
				return Storage(self.key, **self.values)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			warnings.warn(self.AdditionFailureWarning("WARNING! You are strongly advised against adding a Storage "+
						  "instance and a dict/list together, as it may break the Storage "+
						  "instance that is created.",method="__radd__"))
			self.values=other|self.values
			return Storage(self.key, **self.values)
		else:return NotImplemented
			
	def __sub__(self, other: Storage | dict[str, Any]) -> Self:
		"""Defines how to subtract two objects, same type or no."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				skeys: set = set(self.values.keys()) & set(other.values.keys())
				for akey in skeys:
					akey: str
					if akey in self.values:
						del self.values[akey]
					else:
						self.values[akey] = other.values[akey]
				return Storage(self.key, **self.values)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			warnings.warn(self.SubtractionFailureWarning(
				"WARNING! You are strongly advised against subtracting/dividing"+
				" a Storage instance by a dict, as it may break the Storage "+
				"instance that is created.",method="__sub__"))
			skeys: set = set(self.values.keys()) & set(other)
			for akey in skeys:
				akey: str
				if akey in self.values:
					del self.values[akey]
				else:
					self.values[akey] = other.values[akey]
			return Storage(self.key, **self.values)
		else:return NotImplemented

	def __rsub__(self, other: Storage | dict[str, Any]) -> Self:
		"""Defines how to subtract two objects, same type or no."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				skeys: set = set(self.values.keys()) & set(other.values.keys())
				for akey in skeys:
					akey: str
					if akey in self.values:
						del self.values[akey]
					else:
						self.values[akey] = other.values[akey]
				return Storage(self.key, **self.values)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			warnings.warn(self.SubtractionFailureWarning(
				"WARNING! You are strongly advised against subtracting/dividing"+
				" a Storage instance by a dict, as it may break the Storage "+
				"instance that is created.",method="__rsub__"))
			skeys: set = set(self.values.keys()) & set(other)
			for akey in skeys:
				akey: str
				if akey in self.values:
					del self.values[akey]
				else:
					self.values[akey] = other.values[akey]
			return Storage(self.key, **self.values)
		else:return NotImplemented

	def __truediv__(self, other: Storage | dict[str, Any] | int) -> list[Self,...] | Self:
		"""
		Defines how to divide two objects, same type or no.
		Note that attempting to divide a Storage instance by another instance
		or a dictionary (and vice versa) will result in the subtraction of the two.
		"""
		if isinstance(other, (type(self),dict)):return self - other
		elif isinstance(other, int):
			split: float | int = len(self.values.keys())/other
			if other > 9:raise ValueError("Dividing by a number greater than nine is unsupported")
			elif len(self.values.keys()) == split: return [Storage(self.key, **self.values)]
			elif split.is_integer():
				i: int = 0
				rtlist: list[dict | Storage] = []
				while i < split*other:
					nd: dict = {}
					nkey: str = list(self.values.keys())[i]
					nd[nkey]=self.values[nkey]
					i += 1
					while i % split != 0:
						nkey = list(self.values.keys())[i]
						nd.update([str(nkey),self.values[nkey]])
						i += 1
					rtlist.append(nd)
				i = 0
				while i < other: rtlist[i] = Storage(self.key, **rtlist[i]); i+=1
				return rtlist
			else:raise ValueError(f"Cannot divide by number {other} for a list length of {len(self.values.keys())}")
		else:return NotImplemented

	def __rtruediv__(self, other: Storage | dict[str, Any]) -> Self:
		"""
		Defines how to divide two objects, same type or no.
		Note that attempting to divide a Storage instance by another instance
		or a dictionary (and vice versa) will result in the subtraction of the two.
		"""
		if isinstance(other, (type(self),dict)):return other - self
		else:return NotImplemented

	def __and__(self, other: Storage | dict[str, Any]) -> Self | int:
		"""Defines using AND (&) for bitwise operations with Storage instances and dictionaries."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				skeys: set = set(self.values.keys()) & set(other.values.keys())
				if not skeys: return 0
				rtd: dict = {}
				for akey in skeys:
					akey: str
					if akey in self.values:rtd[akey] = self.values[akey]
					if akey in other.values:rtd[akey] = other.values[akey]
				return Storage(self.key, **rtd)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			skeys: set = set(self.values.keys()) & set(other)
			if not skeys: return 0
			rtd: dict = {}
			for akey in skeys:
				akey: str
				if akey in self.values:rtd[akey] = self.values[akey]
				if akey in other.values:rtd[akey] = other.values[akey]
			return Storage(self.key, **rtd)
		else:return NotImplemented

	def __or__(self, other: Storage | dict[str, Any]) -> Self | int:
		"""Defines using OR (|) for bitwise operations with Storage instances and dictionaries."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				skeys: set = set(self.values.keys()) | set(other.values.keys())
				if not skeys: return 0
				rtd: dict = {}
				for akey in skeys:
					akey: str
					if akey in self.values:rtd[akey] = self.values[akey]
					if akey in other.values:rtd[akey] = other.values[akey]
				return Storage(self.key, **rtd)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			skeys: set = set(self.values.keys()) | set(other)
			if not skeys: return 0
			rtd: dict = {}
			for akey in skeys:
				akey: str
				if akey in self.values:rtd[akey] = self.values[akey]
				if akey in other.values:rtd[akey] = other.values[akey]
			return Storage(self.key, **rtd)
		else:return NotImplemented

	def __xor__(self, other: Storage | dict[str, Any]) -> Self | int:
		"""Defines using XOR (^) for bitwise operations with Storage instances and dictionaries."""
		if isinstance(other, type(self)):
			if self.key==other.key:
				skeys: set = set(self.values.keys()) ^ set(other.values.keys())
				if not skeys: return 0
				rtd: dict = {}
				for akey in skeys:
					akey: str
					if akey in self.values:rtd[akey] = self.values[akey]
					if akey in other.values:rtd[akey] = other.values[akey]
				return Storage(self.key, **rtd)
			else:raise ValueError("Both instances must have the same top level key")
		elif isinstance(other, dict):
			skeys: set = set(self.values.keys()) ^ set(other)
			if not skeys: return 0
			rtd: dict = {}
			for akey in skeys:
				akey: str
				if akey in self.values:rtd[akey] = self.values[akey]
				if akey in other.values:rtd[akey] = other.values[akey]
			return Storage(self.key, **rtd)
		else:return NotImplemented

	def __lshift__(self, other: int) -> Self | int:
		"""Defines using left shifting (<<) for bitwise operations with Storage instances."""
		if isinstance(other, int):
			if other > len(self.values.keys()):return 0
			try:
				skeys: list = list(self.values.keys())[other:]
				if not skeys: return 0
				rtd: dict = {}
				for akey in skeys:
					akey: str
					if akey in self.values: rtd[akey] = self.values[akey]
				return Storage(self.key, **rtd)
			except IndexError:
				return 0

	def __rshift__(self, other: int) -> Self | int:
		"""Defines using right shifting (>>) for bitwise operations with Storage instances."""
		if isinstance(other, int):
			if other > len(self.values.keys()):return 0
			try:
				skeys: list = list(self.values.keys())[:-other]
				if not skeys: return 0
				rtd: dict = {}
				for akey in skeys:
					akey: str
					if akey in self.values: rtd[akey] = self.values[akey]
				return Storage(self.key, **rtd)
			except IndexError:
				return 0
				
	def __getitem__(self, key: str | int | slice) -> Any:
		"""Defines how to get an item from the object."""
		if isinstance(key, str):return self.values[key]
		elif isinstance(key,int):return self.values[list(self.values.keys())[key]]
		elif isinstance(key,slice): return [self.values[k] for k in list(self.values.keys())[key]]

	def __setitem__(self, key: str | int, value: Any) -> None:
		"""Defines how to set an item in the object to another value."""
		if isinstance(key, str):self.values[key] = value
		elif isinstance(key, int):self.values[list(self.values.keys())[key]] = value

	def __delitem__(self, key: str | int | slice) -> None:
		"""Defines how to delete an item in the object."""
		if isinstance(key, str): del self.values[key]
		elif isinstance(key, (int,slice)): del self.values[list(self.values.keys())[key]]

	def __len__(self) -> int:
		"""Returns the length of the object."""
		return len(self.values.keys())

	def __contains__(self, item: Any) -> bool:
		"""Defines how the object reacts to the 'in' keyword."""
		return True if item in self.values else False

	def __iter__(self) -> Generator[str|uuid.UUID|dict[str,Any], None, None]:
		"""Defines how the object will act in an iteration loop."""
		counter = 0
		while counter <= len(self.values):
			if counter == 0:yield self.key
			elif counter > 0:yield {list(self.values.keys())[counter-1]: self.values[list(self.values.keys())[counter-1]]}
			counter+=1

	def __getattr__(self, name: Any) -> None:
		"""Fallback function for handling an attempt to call an undefined attribute."""
		cm = difflib.get_close_matches(name,
									   self.__dict__.keys(),
									   n=1,
									   cutoff=0.5)  
		raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'" + 
							 (f". Did you mean '{cm[0]}'?" if cm else ""))

	def __setattr__(self, name: str, value: Any) -> None:
		"""Handles attribute setting attempts."""
		print(f"__setattr__: INFO: Attempting to set '{name}' to '{value}'") 
		super().__setattr__(name, value)

	def __call__(self, **kwargs) -> None:
		"""Defines what happens when an instance is called as a function."""
		self.values.update(kwargs)

	def __enter__(self) -> dict:
		"""Defines the begginning interaction with the 'with' keyword"""
		print("__enter__: INFO: Acquring storage from object") 
		return dict(self.values)

	def __exit__(self, exc_type: type[BaseException] | None,
				 exc_val: BaseException | None,
				 exc_tb: TracebackType | None
				) -> bool:
		"""Defines ending interaction with the 'with' keyword"""
		print("__exit__: INFO: Releasing storage from object")
		if exc_type:print(f"__exit__: ERROR: \n{exc_type}:\n{exc_tb}\n{exc_val}")
		else: return 1

	def __format__(self, format_spec: str) -> str:
		"""Defines interaction with format() and within f-strings."""
		rtn: str = repr(self)
		if format_spec == '.dictf': rtn = str({self.key: {**self.values}}) # full storage
		elif format_spec == '.dictt': rtn = str(self.values) #truncated top level key
		elif format_spec == '.tuplef': rtn = str(tuple({self.key: self.values}))
		elif format_spec == '.tuplet': rtn = str(tuple(self.values))
		elif format_spec == '.key': rtn = str(self.key)
		elif format_spec == '.keys': rtn = str(list(self.values.keys()))
		elif format_spec == '.values': rtn = str(list(self.values.values()))
		return rtn

# Allow importing all Storage.InnerClass()
Delete = Storage.Delete
Load = Storage.Load
Edit = Storage.Edit
