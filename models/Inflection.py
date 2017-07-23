def inflect(request_type, gender, pluralisation):
    value = word_lookup[request_type][pluralisation]
    return value[gender] if isinstance(value, list) else value


word_lookup = {
    # personal pronoun, subject
    'pps1': ['I', 'we'],
    'pps2': ['you', 'you'],
    'pps': [['she', 'he'], 'they'],
    # personal pronoun, object
    'ppo1': ['me', 'us'],
    'ppo2': ['you', 'them'],
    'ppo': [['her', 'him'], 'them'],
    # possessive adjective
    'pa1': ['my', 'our'],
    'pa2': ['your', 'your'],
    'pa': [['his,her'], 'their'],
}