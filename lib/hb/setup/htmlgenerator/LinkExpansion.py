'''
Created on Jul 16, 2015

@author: boris
'''

class LinkExpansion():
    
    '''Expand all substrings of type <<EL|href=link.html|title=Link title|hover=Link hover>> to 
        <a href="link.html" hover="Link hover">Link title</a>
        
        Link placeholder must start with "<EL|" and must end with ">"
        Parameters in the placeholder are of type key===value and are | separated.
        "href" is the only required parameter.
    '''
    
    def __init__(self, strToExpand):
        self._origStr = strToExpand
        
    def expandLinks(self):
        newStr = self._origStr
        import re
        linkPlaceHolders = re.findall("<<EL.*?>>", self._origStr)
        for lph in linkPlaceHolders:
            newStr = newStr.replace(lph, self.processLink(lph))
        return newStr
    
    def processLink(self, linkPlaceHolder):
        
        data = linkPlaceHolder.strip().strip('<<EL|').strip('>>').split('|')
        params = {}
        for param in data:
            assert '===' in param, 'Invalid expandable link place holder %s' % linkPlaceHolder
            key, val = (param.split('===')[0].lower(), param.split('===')[1])
            params[key] = val
            
        processedLink = '<a href="' + params['href'] + '"'
        
        if 'hover' in params:
            processedLink += ' hover="' + params['hover'] + '"'

        if 'onclick' in params:
            processedLink += ' onclick="' + params['onclick'] + '"'

        processedLink += '>'

        if 'title' in params:
            processedLink += params['title']
        else:
            processedLink += params['href']
        
        processedLink += '</a>'
        
        return processedLink

if __name__ == '__main__':
    print LinkExpansion('''Expand link <<EL|href===welcome.html|title===Link title|hover===Link hover>> today!
        And another link <<EL|href===welcome2.html|hover===Link2 hover>>
        
    ''').expandLinks()
