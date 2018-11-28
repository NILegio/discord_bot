from pyparsing import Word, alphanums, Combine, nums


def url_parser(text):
    url_list = []

    def url_append(strg, loc, toks):
        one_url = Word('https://vk.com/') + Word(alphanums + '_') + Word('?w=wall') + Word('-' + nums + '_')
        tokens = one_url.parseString(toks[0])
        url_list.append(tokens[3])

    text_parser = Combine(Word('https://vk.com/') + Word(alphanums + '-?=_')).setParseAction(url_append)
    text_parser.transformString(text)
    return url_list
