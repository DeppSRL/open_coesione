"""
Splits query results list into multiple sublists for template display.
inspired by http://herself.movielady.net/2008/07/16/split-list-to-columns-django-template-tag/

{% list_to_columns people as list 3 %}

"""

from django.template import Library, Node
from django.template.base import TemplateSyntaxError

register = Library()

class SplitListNode(Node):


    def __init__(self, results, cols, new_results, mode):
        self.results, self.cols, self.new_results, self.mode = results, cols, new_results, mode

    def split_seq(self, results, cols=2, mode='vertical'):
        try:
            input = list(results)
        except (ValueError, TypeError):
            return [results]
        splitted = [[] for x in range(cols)]
        if mode == 'horizontal':
            for index, el in enumerate(input):
                splitted[index % cols].append(el)
        elif mode == 'vertical':
            elements_for_columns = len(input) // cols
            for column in range(cols):
                splitted[column] = input[ elements_for_columns*column : elements_for_columns*(column+1)+1 ]
        return splitted
#        start = 0
#        for i in xrange(cols):
#            stop = start + len(results[i::cols])
#            yield results[start:stop]
#            start = stop

    def render(self, context):
        context[self.new_results] = self.split_seq(context[self.results], int(self.cols), self.mode)
        return ''

def list_to_columns(parser, token):
    """Parse template tag: {% list_to_colums results as new_results 2 'vertical' %}"""
    bits = token.contents.split()
    if len(bits) == 5:
        bits.append('vertical')
    if len(bits) != 6:
        raise TemplateSyntaxError, "list_to_columns results as new_results 2"
    if bits[2] != 'as':
        raise TemplateSyntaxError, "second argument to the list_to_columns tag must be 'as'"
    return SplitListNode(bits[1], bits[4], bits[3], bits[5])

list_to_columns = register.tag(list_to_columns)