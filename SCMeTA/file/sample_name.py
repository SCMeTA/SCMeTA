import re

def longest_common_prefix(sample_name: list[str]) -> str:
    """
    Find the longest common prefix in a list of sample names.
    :param sample_name: List of sample names.
    :return: The longest common prefix.
    """
    if not sample_name:
        return ""

    # Initialize the prefix with the first sample name
    prefix = sample_name[0]

    for name in sample_name[1:]:
        # Compare the current name with the prefix
        while not name.startswith(prefix):
            # Shorten the prefix until it matches
            prefix = prefix[:-1]
            if not prefix:
                return ""

    return prefix

def remove_prefix(sample_name: list[str]) -> list[str]:
    """
    Remove the longest common prefix from a list of sample names.
    :param sample_name: List of sample names.
    :return: List of sample names without the common prefix.
    """
    prefix = longest_common_prefix(sample_name)

    if not prefix:
        return sample_name

    # Remove the prefix from each sample name
    return [name[len(prefix):] if name.startswith(prefix) else name for name in sample_name]
