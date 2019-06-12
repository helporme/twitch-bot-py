
def csplit(*args, sep=3):
    values = [] 
    for value in map(str, args):
        #edit value to split on sep characters
        residue = len(value) % sep if len(value) % 3 != 0 else sep
        value = (sep - residue) * '0' + value

        #transform 12345678 to 12,345,678
        value = ','.join(map(''.join, zip(*[iter(value)]*sep)))[sep - residue:]
        values.append(value)

    return iter(values) if len(values) > 1 else values[0]

def cleartext(text):
    stacks = list(zip([pos for pos, sym in enumerate(text) if sym == '<'], [pos for pos, sym in enumerate(text) if sym == '>']))

    for word in [text[stack[0]:stack[1]+1] for stack in stacks]:
        replacable = ''
        if 'href=' in word:
            replacable = word[word.find('href=')+6 : word.find(' rel')-1] + ' ' if len(replacable) > len(word) else ''
            
        text = text.replace(word, replacable)
    
    return text

