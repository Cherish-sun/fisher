def is_key_or_isbn(q):
    '''

    :param q: 传入q, 用来判断q的格式
    :return:
    '''
    key_or_isbn = 'key'
    short_split = str(q).replace('-', '')
    if len(q) == 13 and q.isdigit():
        key_or_isbn = 'isbn'
    if '-' in q and len(short_split) == 10 and short_split.isdigit():
        key_or_isbn = 'isbn'
    return key_or_isbn
