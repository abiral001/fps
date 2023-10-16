def longestPath(G, currentNode):
    path = []
    path.append(currentNode)
    children = getChildren(G, currentNode)
    if len(children) == 0:
        return path
    lrc = children[0]
    path.extend(longestPath(G, lrc))
    for idx, cn in enumerate(children):
        if idx == 0:
            continue
        if cn['startTime'] < lrc['startTime']:
            path.extend(longestPath(G, cn))
    return path


def getChildren(G, currentNode):
    child = []
    for span in G['spans']:
        if span['spanID'] == currentNode['spanID']:
            continue
        for ref in span['references']:
            if ref['spanID'] == currentNode['spanID']:
                child.append(span)
                continue
    return child

def get_cp(trace_data):
    for idx, span in enumerate(trace_data['spans']):
        if len(span['references']) == 0:
            break
    longest_path = longestPath(trace_data, trace_data['spans'][idx])
    return longest_path
