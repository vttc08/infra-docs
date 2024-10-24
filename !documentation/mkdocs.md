---
comments: "true"
update: 2024-10-23T19:38:14-07:00
---
# Mkdocs
### Mkdocs Gotchas
- `yaml` highlighting is broken with `mdx-breakless-lists`
- when using heading `#`, if there are no line breaks between headings, any lists that is after content of the second heading will not be rendered properly, even with `mdx-breakless-lists`
- furthermore, if using lists right after a `yaml` code block, the list will also not be rendered correctly
- ![](assets/Pasted%20image%2020240531235503.png)
- when referencing a subheading in another file, mkdocs uses `[](file.md#heading-with-space)` while obsidian uses `[](file.md#heading%20with%20space)`
- Before switching from lists to normal content, a line break is needed, otherwise the text below will be rendered with a indent
- mkdocs subheadings `[](#subheadings)` must be in lower case

### Admonition/Callouts

???- notes "Mkdocs native callout"
	callout content [mkdocs](mkdocs.md)
	!!! info "Nested"
		Nesting
- `???` is also valid syntax for mkdocs
- `???+` makes the callout collapsible and opens by default, while `???-` makes it closed by default
```
!!! notes "Title"
	content
```
Obsidian callouts requires the plugin `mkdocs-callouts`
>[!notes]+ Obsidian Native Callout
> Callout content [mkdocs](mkdocs.md)
> >[!notes] Nested callout
> >callout

```
> [!notes]+/- Callout title
> Callout content
```
- obsidian callout syntax also follows the same `+`,`-` for collapsing, it is to be inserted after the brackets

Available callouts include `notes`, `info`, `warning`, `danger`, `success`, `failure`, `example`, `abstract`, `tip`, `question`, `bug`. 
![](assets/Pasted%20image%2020240601000413.png)

### Keys, Caret, Mark, Tilde
**Keys**
`++ctrl+alt+plus++`
++ctrl+alt+plus++
![](assets/Pasted%20image%2020240601001447.png)
==mark highlighting==
~~tilde strikethrough~~

### Tabbed Content
=== "Tab 1"
	Tab 1 content [mkdocs](mkdocs.md)
	Second line here.
=== "Tab 2"
	Tab 2 content
```
=== "Tab Name"
	Tab content
```
![](assets/Pasted%20image%2020240601001843.png)
- not supported in obsidian

### attr_list
**Fancy Buttons**
[mkdocs](mkdocs.md){ .md-button }
`[button text](link.md){ .md-button }`
![](assets/Pasted%20image%2020240601002119.png)
**Tooltip**
I'm a [tooltip](https://google.com "text to show when hovered") that you can hover or click.
`[tooltip](https://link "hover text")`
![](assets/Pasted%20image%2020240601002401.png)
**Annotation**
I'm an annotation, but you need to click the plus icon (1) to show. (2) 
{ .annotate }
1. annotation 1
2. annotation 2
```
Annotation location 1 (1), location (2)
{ .annotate }
1. annotation text to be shown
```
![](assets/Pasted%20image%2020240601002809.png)

**Footnote**
Insert footnote like `[^1]` [^1]
- for inserting footnote `[^1]`
- `[^1]:` at the end to explain the footnote; not supported in obsidian

### Code Highlighting
```python
from python import python
python.run(arg1=123, arg2="mystr")[2]
```

```shell
#!/bin/bash
var="myvar"
echo $var+3
```

```yaml
# yaml highlighting has to be `yaml` not `yml` and it's broken
---
version: "2.1"
services:
  clarkson:
    image: lscr.io/linuxserver/clarkson
    container_name: clarkson
    environment:
      - PUID=1000
      - PGID=1000
    ports:
      - 3000:3000
    restart: unless-stopped
```
[^1]: explaining the footnote.