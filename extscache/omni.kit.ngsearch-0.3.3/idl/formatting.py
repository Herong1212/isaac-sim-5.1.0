import re


def format_doc(comment, line_limit, indent, sep=" "):
    comments = []
    limit = line_limit - indent
    for line in comment.split("\n"):
        while len(line) > limit:
            last_space = line[:limit].rindex(sep)
            comments.append(line[:last_space])
            line = line[last_space + 1:]
        comments.append(line)
    return comments


snake_case = re.compile(r"(.*?)_([a-zA-Z])")
camel_case = re.compile(r"(.*?)([A-Z])")
abbr_re = re.compile(r"(.*?)([A-Z]{2,})")


def camel(name):
    def repl(match):
        return match.group(1) + match.group(2).upper()
    return snake_case.sub(repl, name)


def underscore(name):
    def repl(match):
        prefix = match.group(1)
        matched_word = match.group(2).lower()
        if prefix:
            return prefix + "_" + matched_word
        return matched_word
    abbr = abbr_re.sub(repl, name)
    result = camel_case.sub(repl, abbr)
    return result


def pascal(name):
    return underscore(name).title().replace("_", "")
