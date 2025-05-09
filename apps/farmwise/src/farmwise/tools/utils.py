from __future__ import annotations


def copy_doc(from_func):
    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__
        return to_func

    return decorator


def join_with(words, join_word="or"):
    if not words:
        return ""
    if len(words) == 1:
        return words[0]
    if len(words) == 2:
        return f" {join_word} ".join(words)
    return ", ".join(words[:-1]) + f" {join_word} " + words[-1]
