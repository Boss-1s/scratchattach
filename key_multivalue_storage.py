import os
import json
import uuid
import warnings
import logging
from typing import Dict, Any, Optional, Type, List

logging.basicConfig(level=logging.WARNING)
logging.captureWarnings(True)

__all__ = ["Storage", "Storage.Delete", "Storage.Load", "Storage.Edit"]

class _KeyNotFoundError(Exception):
	"""Custom exception raised when a key is not found."""
	def __init__(self, file: str, mkey: str | uuid.UUID, message="") -> None:
		self.mkey = mkey
		self.file = file
		self.message = f"The following key was not found in {file}: {mkey}" if message == "" else message
		super().__init__(self.message)

class Storage:
	"""
	Class for monokey-multivalue storage.
	Developed for the project ScratchChat by Boss_1s -> https://scratch.mit.edu/projects/1051418168
	Used in conjuction with scratchattach.
	
	Usage:
	Storage(key: str, kwargs1: Any, kwargs2: Any...) -> Create an instance of the Storage class to store
	|
	| __all__(\\ = not public)
	|  
	| Storage.__init__()
	|
	| Storage.self._dprint(***)(\\)
	| Storage._encode(***)(\\)
	| Storage._decode(***)(\\)
	| Storage._to_dict(***)(\\)
	| Storage._from_dict(***)(\\)
	| Storage.__store(***)(\\)
	| Storage.__is_filtered_warning(***)(\\)
	|
	| Storage.store(file_path: str) -> Stores created instance into a JSON file
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
	| Storage.__str__()
	"""
	
	#self.variable typing hints
	key: str | uuid.UUID
	values: Dict[str, Any]
	
	#Define public and private methods/classes
	__all__ = ["store", "DeleteWarning", "Load", "Edit", "Delete", "__str__"]
	
	def __init__(self, key: str, **kwargs: Any) -> None:
		"""initiate instance paramaters"""
		self.key = str(key) if isinstance(key, uuid.UUID) else key
		self.values = kwargs
	
	@staticmethod
	def _dprint(string: Any) -> None:
		"""Double-prints by echoing in shell and using print command."""
		print(string)
		os.system(f"echo {string}")
	
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
	def _decode(string: Any) -> str:
		"""Decodes a value encoded with Storage._encode"""
		
		if not isinstance(string, (str, int)): # Accept encoded int or its string repr
			raise TypeError("Expected encoded string or integer for decoding.")
	
		to_decode=str(string)
		
		char="""`1234657809=-\\][p';/.,lokimnjuyhbtfcvgrs edxzawq~+_)(*&^T$%@!#REDFGSWAQZXVCBNHYUJMKI<>LOP:{}|"?><"""
		i=0
		output=''
		while i < len(to_decode):
			totalchars=int(to_decode[i])
			#self._dprint(f"Debug: totalchars {totalchars}")
			currentchar=int(to_decode[i+1:i+1+totalchars])
			#self._dprint(f"Debug: currentchar {currentchar}")
			#Bounds Check
			if not (0 <= currentchar-1 < len(char)):
				raise ValueError(f"Decoding error: Index {currentchar - 1} out of bounds for character map.")
			output=f"{output}{char[currentchar-1]}"
			i=i+1+totalchars
		return output
	
	def _to_dict(self) -> Dict[str, Dict[str, Any]]:
		"""Converts key-multivalue pair into a dict for json dumping"""
		encoded_values: Dict[str, Any] = {}
		for prop_key, prop_value in self.values.items():
			if not (type(self.values.items) is str):
				encoded_values[prop_key] = self._encode(prop_value) # Use self._encode
			else:
				encoded_values[prop_key] = prop_value #skip if not a string, for example timestamps
		
		return {
			self.key: encoded_values
		}
	
	@classmethod
	def _from_dict(cls, data_dict: Dict[str, Dict[str, Any]], raw: bool=False) -> 'Storage':
		"""Class method that extracts data from a dict into seperate key-multivalue pairs, decoding values in the process."""
		
		if not isinstance(data_dict, dict) or len(data_dict) != 1:
			raise ValueError("Expected a dictionary with a single top-level key.")
		
		top_level_key: str = list(data_dict.keys())[0]
		og_nested_values: Dict[str, Any] = data_dict[top_level_key]
		
		if not isinstance(og_nested_values, dict):
			raise ValueError("Expected nested values to be a dictionary.")
	
		if not raw:
		  decoded_values: Dict[str, Any] = {}
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
	def __store(file_path: str, dict_to_dump: Dict[str, Dict[str, Any]], indent: int=4) -> None:
		"""For private use by delete class, works just like Storage.store() but dict is already created, so no instance is required."""
		"""Store a key-multivalue pair into a json file."""
		all_data: Dict[str, Dict[str, Any]] = {}
		try:
			with open(file_path, "r") as f:
				all_data = json.load(f)
		except FileNotFoundError:
			Storage._dprint(f"File '{file_path}' not found. Creating a new one.")
		except json.JSONDecodeError:
			warnings.warn(f"Warning: File '{file_path}' contains invalid JSON. Overwriting.", SyntaxWarning)
			all_data = {}
	
		all_data.update(dict_to_dump)
	
		try:
			with open(file_path, "w") as f:
				json.dump(all_data, f, indent=indent)
			Storage._dprint(f"Data for key '{list(dict_to_dump.keys())[0]}' stored successfully in '{file_path}'.")
		except IOError as e:
			Storage._dprint(f"Error writing to file '{file_path}': {e}")
	
	@staticmethod
	def __is_warning_category_ignored(category: Any) -> bool:
		for action, message, cat, module, lineno in warnings.filters:
			if action == 'ignore' and category==cat:
				return True
		return False
		
	def store(self, file_path: str, indent: int=4) -> None:
		"""Store a key-multivalue pair into a json file."""
		all_data: Dict[str, Dict[str, Any]] = {}
		try:
			with open(file_path, "r") as f:
				all_data = json.load(f)
		except FileNotFoundError:
			self._dprint(f"File '{file_path}' not found. Creating a new one.")
		except json.JSONDecodeError:
			warnings.warn(f"Warning: File '{file_path}' contains invalid JSON. Overwriting.", SyntaxWarning)
			all_data = {}
		
		if ".json" not in file_path:
			fp = str(file_path) + ".json"
		
		all_data.update(self._to_dict())
	
		try:
			with open(file_path, "w") as f:
				json.dump(all_data, f, indent=indent)
			self._dprint(f"Data for key '{self.key}' stored successfully in '{file_path}'.")
		except IOError as e:
			self._dprint(f"Error writing to file '{file_path}': {e}")
			
	class DeleteWarning(UserWarning):
		"""Custom warning when attempting to delete the contents of a whole database."""
		pass
	
	class Load:
		__all__ = ["by_key", "by_index", "keys", "values"]
	  
		@classmethod
		def by_key(cls, file_path: str, key: str | uuid.UUID, raw: bool=False) -> Optional['Storage']:
			"""Load a json file and find the key to extract a single key-multivalue pair and its values"""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load with key '{key}' - file '{file_path}' does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load with key '{key}' - file '{file_path}' contains invalid JSON.")
				return None
	
			#Debug
			#Storage._dprint(f"DEBUG: Data loaded from '{file_path}': {loaded_data}")
			#Storage._dprint(f"DEBUG: Keys in loaded_data: {loaded_data.keys()}")
			#Storage._dprint(f"DEBUG: Type of loaded_data keys: {[type(k) for k in loaded_data.keys()]}") # Add this line
			#Storage._dprint(f"DEBUG: Key being searched for: '{key}'")
			#Storage._dprint(f"DEBUG: Type of search key: {type(key)}") # Add this line
		  
			# Super-detailed comparison check
			#found_in_keys = False
			#for k in loaded_data.keys():
				#Storage._dprint(f"  Comparing '{key}' (len={len(key)}, repr={repr(key)}) with loaded key '{k}' (len={len(k)}, repr={repr(k)})")
				#if key == k:
					#found_in_keys = True
					#Storage._dprint(f"  Match found for key '{key}'!")
					#break
			
			if key in loaded_data: #found_in_keys: #Use the flag from the detailed comparison
				try:
					return Storage._from_dict({key: loaded_data[key]}, raw) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{key}': {e}")
					return None
			else:
				raise _KeyNotFoundError(file_path, key)
	
		@classmethod
		def by_index(cls, file_path: str, index: int, raw: bool=False) -> Optional['Storage']:
			"""Load a json file and find the index at which to extract a single key-multivalue pair and its values."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load by index '{index}' - file '{file_path}' does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load by index '{index}' - file '{file_path}' contains invalid JSON.")
				return None
	
			keys = list(loaded_data.keys())
	
			# Check if the provided index is valid
			if not (0 <= index < len(keys)):
				Storage._dprint(f"Index '{index}' is out of bounds for the keys in '{file_path}'. Available keys: {len(keys)}")
				return None
	
			# Get the key at the specified index
			target_key: str = keys[index]
			
			# Now, reconstruct the Storage object using the extracted key and its corresponding data
			if target_key in loaded_data: # This check is technically redundant if index is valid, but good for robustness
				try:
					return Storage._from_dict({target_key: loaded_data[target_key]}, raw) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{target_key}' at index '{index}': {e}")
					return None
			else: # This path should ideally not be hit if the index check is correct
				raise _KeyNotFoundError(file_path, target_key, f"Key '{target_key}' unexpectedly not found in loaded data for index '{index}'.")
	
		@classmethod
		def keys(cls, file_path: str) -> Optional[List[str]]:
			"""Load a json file and returns the keys of that file."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			return list(loaded_data.keys())
	
		@classmethod
		def values(cls, file_path: str, key: str | uuid.UUID, keys: bool=False, raw: bool=True) -> Optional[List[str]]:
			"""
			Loads a json file and returns the values under the inputed key. Unlike other loading methods, this one returns the raw values by default.
			Keys can also be returned as a key-value pair if keys=True.
			"""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			if key in loaded_data:
				try:
				   subsection: Dict[str, Dict[str, Any]] = Storage._from_dict({key: loaded_data[key]}, raw) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{key}': {e}")
					return None
			else:
				raise _KeyNotFoundError(file_path, key)
	
			items: List[str] = []
			for key, val in subsection.values.items():
				if keys:
					items.append(f"{key}: {val}")
				else:
					items.append(val)
					#Storage._dprint(f"DEBUG: {val}")
			return items
	
	class Edit:
		__all__ = ["propkey", "propval", "key"]
	
		@classmethod
		def propkey(cls, file_path: str, top_lv_key: str | uuid.UUID, oldpropkey: str, newpropkey: str, new: bool=True) -> None:
			"""Edits the name of subkey within a key within a JSON file. The value of that subkey does not change."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			if top_lv_key in loaded_data:
				try:
				   subsection: Dict[str, Dict[str, Any]] = Storage._from_dict({top_lv_key: loaded_data[top_lv_key]}) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{top_level_key}': {e}")
					return None
			else:
				raise _KeyNotFoundError(file_path, top_lv_key)
	
			items: Dict[str, Any] = {}
			#allkeys: List[str] = []
			#allvalues: List[Any] = []
			if oldpropkey in subsection:
				for propkey, propval in subsection.values.items():
					if propkey == oldpropkey:
						items[newpropkey] = propval
						#allkeys.append(newpropkey)
						#allvalues.append(propval)
					else:
						items[propkey] = propval
						#allkeys.append(propkey)
						#allvalues.append(propval)
			elif new:
				Storage._dprint(f"Subkey {oldpropkey} was not found. Creating a new subkey under the name"+
					  " {newpropkey} with value '' (override this with new=False, will raise exception)")
				for propkey, propval in subsection.values.items():
					items[propkey] = propval
				items[newpropkey] = ''
			else:
				raise _KeyNotFoundError(file_path, oldpropkey)
	
			to_dump: Dict[str, Dict[str, Any]] = {
				top_lv_key: items
			}
	
			Storage._Storage__store(file_path, to_dump)
			Storage._dprint(f"Sucessfully renamed {oldpropkey} to {newpropkey}.")
	
		@classmethod
		def propval(cls, file_path: str, top_lv_key: str | uuid.UUID, propkey: str, newval: str) -> None:
			"""Edits the value of a subkey within a key within a JSON file. The subkey of that value does not change."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			if top_lv_key in loaded_data:
				try:
				   subsection: Dict[str, Dict[str, Any]] = Storage._from_dict({top_lv_key: loaded_data[top_lv_key]}) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{top_lv_key}': {e}")
					return None
			else:
				raise _KeyNotFoundError(file_path, top_lv_key)
	
			items: Dict[str, Any] = {}
			#allkeys: List[str] = []
			#allvalues: List[Any] = []
			for propkey1, propval in subsection.values.items():
				if propkey == propkey1:
					oldval = propval
					items[propkey] = newval
					#allkeys.append(propkey)
					#allvalues.append(newval)
				else:
					items[propkey1] = propval
					#allkeys.append(propkey1)
					#allvalues.append(propval)
	
			to_dump: Dict[str, Dict[str, Any]] = {
				top_lv_key: items
			}
	
			Storage._Storage__store(file_path, to_dump)
			Storage._dprint(f"Sucessfully changed value {oldval} to {newval} under key {top_lv_key}.{propkey}.")
	
		@classmethod
		def key(cls, file_path: str, oldkey: str | uuid.UUID, newkey: str | uuid.UUID) -> None:
			"""Deletes a key-multivalue pair and its values within a JSON file. 
			Does NOT create a new instance of Storage, you will have to regrab
			the values to see the changes."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			#Storage._dprint(f"DEBUG: {loaded_data.keys()}")
			#Storage._dprint(f"DEBUG: {loaded_data.values()}")
			#Storage._dprint(f"DEBUG: {loaded_data}")
	
			if oldkey in loaded_data:
				loaded_data = {
					newkey if key == oldkey else key: value
					for key, value in loaded_data.items()
				}
				Storage._dprint(f"DEBUG: New dictionary: {loaded_data}")
				try:
					with open(file_path, "w") as f:
						json.dump(loaded_data, f)
						Storage._dprint(f"Successfully changed key '{oldkey}' to '{newkey}'.")
				except IOError as e:
					Storage._dprint(f"Error writing to file '{file_path}' after deletion: {e}")
			else:
				raise _KeyNotFoundError(file_path, oldkey)
	
	class Delete:
		__all__ = ["by_propkey", "by_key", "all"]
	  
		@classmethod
		def by_propkey(cls, file_path: str, top_level_key: str | uuid.UUID, property_key: str) -> None:
			"""Deletes a property within a top-level key in the JSON file. Does NOT create a new instance of Storage, you will have to regrab the values to see the changes."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
			
			if top_level_key in loaded_data:
				try:
				   subsection: Dict[str, Dict[str, Any]] = Storage._from_dict({top_level_key: loaded_data[top_level_key]}) 
				except ValueError as e:
					Storage._dprint(f"Error reconstructing object for key '{top_level_key}': {e}")
					return None
			else:
				raise _KeyNotFoundError(file_path, top_level_key)
			
			items: Dict[str, Any] = {}
			#allkeys: List[str] = []
			#allvalues: List[Any] = []
			for propkey, propval in subsection.values.items():
				if propkey != property_key:
					items[propkey] = propval
					#allkeys.append(propkey)
					#allvalues.append(propval)
	
			#Storage._dprint(f"DEBUG: {items}")
			#Storage._dprint(type(items))
			#Storage._dprint(f"DEBUG: {subsection}")
			#Storage._dprint(f"DEBUG: {top_level_key}")
			#Storage._dprint(type(top_level_key))
		  
			to_dump: Dict[str, Dict[str, Any]] = {
				top_level_key: items
			}
	
			#Storage._dprint(f"DEBUG: {to_dump}")
	
			Storage._Storage__store(file_path, to_dump)
	
		@classmethod
		def by_key(cls, file_path: str, key: str | uuid.UUID) -> None:
			"""Deletes a key-multivalue pair and its values within a JSON file. 
			Does NOT create a new instance of Storage, you will have to regrab the 
			values to see the changes."""
			try:
				with open(file_path, "r") as f:
					loaded_data: Dict[str, Dict[str, Any]] = json.load(f)
			except FileNotFoundError:
				Storage._dprint(f"Failed to load file '{file_path}': does not exist.")
				return None
			except json.JSONDecodeError:
				Storage._dprint(f"Failed to load file '{file_path}': contains invalid JSON.")
				return None
	
			#Storage._dprint(f"DEBUG: {loaded_data.keys()}")
			#Storage._dprint(f"DEBUG: {loaded_data.values()}")
			#Storage._dprint(f"DEBUG: {loaded_data}")
	
			if key in loaded_data:
				del loaded_data[key]
				try:
					with open(file_path, "w") as f:
						json.dump(loaded_data, f)
						Storage._dprint(f"Successfully deleted key '{key}' from '{file_path}'.")
				except IOError as e:
					Storage._dprint(f"Error writing to file '{file_path}' after deletion: {e}")
			else:
				raise _KeyNotFoundError(file_path, key)
	
			
		@staticmethod
		def all(file_path: str, warn: bool=True) -> None:
			if Storage._Storage__is_warning_category_ignored("DeleteWarning") or warn:
				warnings.warn(f"You are about to delete ALL of the data inside the file {file_path}. "+ 
							  "This is an irreversible action! If you are COMPLETELY CERTAIN about deleting all the data, "+
							  "add Storage.Delete.all(file_path, warn=False) to your script. If you never want to see this warning again, "+
							  "add warnings.filterwarning(category=Storage.DeleteWarning) to your script.", 
							  DeleteWarning)
			else:
				with open(file_path, "w") as f:
					json.dump({}, f)
					Storage._dprint(f"Deleted all data from {file_path} sucessfully.")
					return None
	
	def __str__(self) -> str:
		"""Defines how the object should be represented as a string, useful for printing the whole output in the desired format."""
		# Format the nested dictionary directly
		values_str = ', '.join([f"{prop}: {repr(value)}" for prop, value in self.values.items()])
		return f"{self.key}: {{{values_str}}}"

# Allow importing all Storage.InnerClass()
Delete = Storage.Delete
Load = Storage.Load
Edit = Storage.Edit
