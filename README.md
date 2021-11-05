shortcode for mkdocs
====================


Templates and Shortcodes
------------------------

This plugin adds shortcodes and templates to mkdocs. In context, shortcode and templates are:

* **theme**: mkdocs already supports themes. Here, the style of the complete website with all its pages is defined.
* **template**: A markdown-file in in the docs/-folder can define its template. In this case a special HTML is loaded ad template for that markdown. If you observe magazines for example, there are a limited number of structures of pages, like image on the left side, info-box on the right and so on. Templates are that for mkdocs. Templates require, that you define template-specific blocks, like image-block or infobox-block
* **shortcode**: These are the lowest of the reusable components. One shortcode generates multiple HTML-elements. This is useful, if you want to extend the markdown language in an easy way. Examples are blocks where the image is left of the text.

The new directives (think markdown-extensions) are designed in such a way that they are backwards-compatible with markdown. The idea is that they are interpreded as markdown-comments of normal compilers.


Shortcode: Example
------------------

### Usage

Usage of an shortcode looks like:

```
... some previous markdown

[start]: with_image (pos="right", src="https://dummyimage.com/400x600/eee/aaa")

## How it works 
1. This is a good point
2. everything is markdown
3. And yet another point

[end]: with_image

... some other markdown continues
```

Note, that we wrap some content with the shortcode and pass some parameters. The `pos` argument says, that the image defined in `src` should be renderd right of the wrapped content. To see, how this is done, see the next section.

### Definition

You can create shortcode very easly, by creating a jinja2-html-file under `./shortcodes/` with the name of the shortcode. In this example we defined `./shortcoded/with_image.html`:

```
<div class="row {{class}} mt-5 with-image">
    {% if pos == "left" %}
    <div class="col-md-5">
        <img src="{{src}}" alt="alt" />
    </div>
    <div class="col-md-7">
        {{content}}
    </div>
    {% else %}
    <div class="col-md-7">
        {{content}}
    </div>
    <div class="col-md-2">
        <img src="{{src}}" alt="alt" />
    </div>
    {% endif %}
</div>
```

Note, that we can use the kwargs-paramters with `{{parameter-name}}` as usual in jinja2 and there is also the special variable `{{content}}` which are the lines beteen start and end.


Template: Example
-----------------

### Usage

We can define one template per markdown-file. The template defines blocks, that we can fill if we want. This can look for example like this.

```
[template]: promo1 (color="red")


[block]: mainimage

![Some image](https://dummyimage.com/800x400/eee/aaa)

[endblock]: mainimage



[block]: content

# Markdown

here comes the normal markdown code. This is wrapped within the content. The whole block gets placed at the proper position in the output by the template

[endblock]: content

```

This snipped uses the template `promo1`. Note, that you can use parameters as well. It is important to understand that you only fill out the content of the blocks. The blocks themself are placed by the template at the correct position. There are normally a few templates in a project and many sites use them. If you want to make a consistent change, you have to change only one template (for example move all info-boxes from left to right).

### Definition

Defining templates works by creating a jinja2-html-file under the folder `./shortcodes/templates`. In this example there is a file `./shortcodes/templates/promo1.html` with this content:

```
<div class="row" style="border: 1px solid {{color or 'white'}}">
    <div class="col-md-12 main-image-container">
        {% block mainimage %}
        {% endblock %}
    </div>
</div>
<div class="row">
    <div class="col-md-12">
        {% block content %}
        {% endblock content %}
    </div>
</div>
```

You can see that this template just adds the image-block before the content and wraps the content a little bit. Also you can see the usage of the specified parameter `color` which you can access as a normal variable using `jinja2`. 