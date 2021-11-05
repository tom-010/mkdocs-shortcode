from os import replace
import jinja2
from mkdocs.plugins import BasePlugin
import re


needle = ' 28298323needle123234donotedit '

pattern = r'\[ *(?:start|end|element) *\] *:.*'

type_pattern = r'\[ *(start|end|element) *\]'
function_pattern = r'\[.*\] *:([^\()]*)'
parameters_pattern = r'\[.*\] *:.*\((.*)\)'

block_pattern = r'\[ *(?:template|block|endblock) *\] *:.*'
block_type_pattern = r'\[ *(template|block|endblock) *\]'

def parse_params(s):
    parameters = re.findall(parameters_pattern, s)
    if parameters:
        parameters = parameters[0].strip()
        parameters = [p.strip() for p in parameters.split(',')]
    else:
        parameters = []
    
    args = []
    kwargs = {}

    for p in parameters:
        if '=' in p:
            key, value = p.split('=', maxsplit=1)
            kwargs[key] = eval(value)
        else:
            args.append(eval(p))
    return args, kwargs

class TemplateShortcode:

    template_shortcodes = {
        'template': "{% extends '{{fun}}.html' %}",
        'block': "{% block {{fun}} %}",
        'endblock': "{% endblock {{fun}} %}"
    }

    @staticmethod
    def from_str(s):
        block_type = re.findall(block_type_pattern, s)[0].strip()
        fun = re.findall(function_pattern, s)[0].strip()
        args, kwargs = parse_params(s)
        return TemplateShortcode(fun, block_type, args, kwargs)

    def __init__(self, fun, block_type, args, kwargs):
        self.fun = fun
        self.block_type = block_type
        self.args = args
        self.kwargs = kwargs

    def generate_html(self):
        res = self.template_shortcodes[self.block_type].replace('{{fun}}', self.fun)
        return res


class Shortcode:

    @staticmethod
    def from_str(s):
        shortcode_type = re.findall(type_pattern, s)[0].strip()
        fun = re.findall(function_pattern, s)[0].strip()
        args, kwargs = parse_params(s)
        return Shortcode(shortcode_type, fun, args, kwargs)

    def __init__(self, shortcode_type, fun, args, kwargs):
        self.shortcode_type = shortcode_type
        self.fun = fun
        self.args = args
        self.kwargs = kwargs
        self.content = []
            
    
    def generate_html(self):
        filename = './shortcodes/' + self.fun + '.html'

        try:
            with open(filename) as file_:
                template = file_.read()
        except FileNotFoundError:
            return None

        

        template = template.replace('<', '\n<!-- '+needle+'<')
        template = template.replace('>', '>'+ needle + ' -->')
        template = jinja2.Template(template)

        kwargs = {**self.kwargs}
        kwargs['content'] = '\n'.join(self.content)
        for idx, arg in enumerate(self.args):
            kwargs[f'var{idx+1}'] = arg

        res = template.render(**kwargs)

        return res

    def __repr__(self):
        return self.fun


class ShortcodePlugin(BasePlugin):
    

    def on_page_markdown(self, markdown, page, config, files):
        res = markdown
        res = self.process_shortcodes(res)
        res = self.mask_blocks(res)
        return res

    def mask_blocks(self, markdown):
        lines = markdown.split('\n')
        for idx, line in enumerate(lines):
            res = re.findall(block_pattern, line)
            if res:
                lines[idx] = '<!-- ' + needle + line + needle + ' -->'
        return '\n'.join(lines)

    def process_blocks(self, html):
        lines = html.split('\n')

        resulting_lines = []
        kwargs = {}
        for line in lines:
            res = re.findall(block_pattern, line)
            if res:
                s = TemplateShortcode.from_str(res[0])
                if s.block_type == 'template':
                    kwargs = {**kwargs, **s.kwargs}
                html = s.generate_html()
                resulting_lines += html.split('\n')
            else:
                resulting_lines.append(line)


        env = jinja2.Environment(loader=jinja2.FileSystemLoader('./shortcodes/templates/'))
        template = env.from_string('\n'.join(resulting_lines))

        res = template.render(**kwargs)
        return res

    def process_shortcodes(self, markdown):

        resulting_lines = []
        current_shortcode = None 

        for line in markdown.split('\n'):
            meta_line = re.findall(type_pattern, line)
            line_type = meta_line[0].strip() if meta_line else 'content'
            
            if line_type == 'start' or line_type == 'element':
                current_shortcode = Shortcode.from_str(line)
            
            if line_type == 'content':
                if current_shortcode:
                    current_shortcode.content.append(line)
                else:
                    resulting_lines.append(line)

            if line_type == 'end' or line_type == 'element':
                html = current_shortcode.generate_html()
                if html:
                    resulting_lines += html.split('\n')
            
                current_shortcode = None


        return '\n'.join(resulting_lines)


    def unmask(self, html):
        lines = html.split('\n')
        for idx, line in enumerate(lines):
            
            line = line.replace('<!-- ' + needle, '')
            line = line.replace(needle + ' -->', '')
            lines[idx] = line


        return '\n'.join(lines)

    def on_page_content(self, html, page, config, files):
        res = html
        res = self.unmask(res)
        res = self.process_blocks(res)
        return res


        
    def to_lines_with_needles(self, html):
        lines = html.split('\n')
        lines = ['<!-- ' + needle + line + needle + ' -->' for line in lines]
        lines += ['\n']
        return lines