"""
Instance class
===============
"""
import copy
import uuid
import hashlib
from typing import List

class Instance:
    def __init__(self, *, query: str = None, jailbreak_prompt: str = None, reference_responses: 'List[str]' = None, target_responses: 'List[str]' = None, eval_results: list = None, parents: list = None, children: list = None, attack_attrs = None, **kwargs):
        """
        Initializes an instance with various attributes relevant to the jailbreaking context.

        :param str query: The query associated with the instance.
        :param str jailbreak_prompt: The prompt related to jailbreaking, usually a formatted string.
        :param List[str] reference_responses: A list of reference responses for comparison.
        :param List[str] target_responses: A list of target responses generated by the model.
        :param List[str] eval_results: A list of evaluation results.
        :param List[~Instance] parents: A list of parent instances, indicating the lineage or history.
        :param List[~Instance] children: A list of child instances, indicating derived or subsequent instances.
        :param Dict attack_attrs: A dictionary for storing various attributes related to the attack process.
        :param kwargs: Additional keyword arguments.
        """
        self._data = {}
        self.query = query
        self.jailbreak_prompt = jailbreak_prompt
        self.reference_responses = reference_responses or []
        self.target_responses = target_responses or []
        self.eval_results = eval_results or []
        self.parents = parents or []
        self.children = children or []
        self.index: int = None

        self.attack_attrs = attack_attrs or {'Mutation': None, 'query_class': None}
        self._data.update(**kwargs)

        # Generate a deterministic id based on query and jailbreak_prompt
        self.id = self._generate_id()

    def _generate_id(self):
        """Generate a deterministic id based on query and jailbreak_prompt."""
        content = f"{self.query}|{self.jailbreak_prompt}"
        return hashlib.md5(content.encode()).hexdigest()

    def copy(self):
        """
        Creates a deep copy of the instance.

        :return ~Instance : A new instance that is a deep copy of the current instance.
        """
        new_Instance = Instance(
            query=self.query,
            jailbreak_prompt=self.jailbreak_prompt,
            reference_responses=self.reference_responses.copy(),
            target_responses=self.target_responses.copy(),
            eval_results=self.eval_results.copy(),
            parents=[i for i in self.parents],
            children=[i for i in self.children],
            attack_attrs=copy.deepcopy(self.attack_attrs))
        rest_data = {key: value for key, value in self._data.items() if key not in new_Instance._data}
        new_Instance._data.update(copy.deepcopy(rest_data))
        return new_Instance

    def delete(self, *keys):
        """
        Deletes specified attributes from the instance.

        :param keys: The keys of the attributes to be deleted.
        """
        for key in keys:
            del self._data[key]

    def to_dict(self):
        """
        Converts the instance into a dictionary, excluding parents and children.

        :return: A dictionary representation of the instance.
        """
        temp_parents = self._data.pop('parents', None)
        temp_children = self._data.pop('children', None)
        temp_return =  copy.deepcopy(self._data)
        if temp_parents is not None:
            self._data['parents'] = temp_parents
        if temp_children is not None:
            self._data['children'] = temp_children
        return temp_return

    @property
    def num_query(self):
        """
        Calculates the total number of 'jailbreak' occurrences from the eval_results.

        :return int: The sum of jailbreak results.
        """
        return len(self.target_responses)

    @property
    def num_jailbreak(self):
        """
        Calculates the total number of 'jailbreak' occurrences from the eval_results.

        :return int: The sum of jailbreak results.
        """
        return sum(self.eval_results)

    @property
    def num_reject(self):
        """
        Calculates the number of rejections (non-jailbreak occurrences) from the eval_results.

        :return int: The count of reject results.
        """
        return len(self.eval_results) - sum(self.eval_results)

    def __getattr__(self, name):
        if '_data' in self.__dict__:  # Ensure _data exists in the object's dictionary
            try:
                return self._data[name]
            except KeyError:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name == '_data':
            super().__setattr__(name, value)
        else:
            self._data[name] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

    def __str__(self):
        return self._data.__str__()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()

    def items(self):
        return self._data.items()

    def __iter__(self):
        return self._data.__iter__()


if __name__ == '__main__':
    instance1 = Instance(query='test', jailbreak_prompt='test_prompt')
    instance2 = Instance(query='test', jailbreak_prompt='test_prompt', reference_responses=['test1', 'test2'],
                         target_responses=['test1', 'test2'], eval_results=[1, 1])
    instance2.parents.append(instance1)
    instance1.children.append(instance2)

    print(instance1.to_dict())
    print(instance2.to_dict())
