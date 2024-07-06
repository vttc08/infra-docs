---
date: 2023-09-19T21:15:30.000000Z
update: 2024-07-01T13:35:44-07:00
comments: "true"
---
# OliveTin

OliveTin exposes a webpage with buttons that execute shell command (eg. docker, scripts) on the server and allow others for easy access. It should be used internally only.

**Installation**

Download the correct file from this site. [https://github.com/OliveTin/OliveTin/releases](https://github.com/OliveTin/OliveTin/releases) *OliveTin\_linux\_amd64.deb*

Go to the directory and install the package.

```
sudo dpkg -i OliveTin…​deb
sudo systemctl enable --now OliveTin
```

### Configuration

The configuration file is located at `<em>/etc/OliveTin/config.yaml </em>`

Example Configuration

```yaml
listenAddressSingleHTTPFrontend: 0.0.0.0:1378 # set the port of OliveTin to 1378

# Choose from INFO (default), WARN and DEBUG
logLevel: "INFO"

# Actions (buttons) to show up on the WebUI:
actions:
  # This will run a simple script that you create.
- title: Update Music
  shell: /home/karis/scripts/script
  icon: '&#127925'


```

More possible configurations (many are not possible on Docker)

Execute a shell command with textbox input.

```yaml
- title: Restart a Docker CT
  icon: '<img src = "icons/restart.png" width="48px" />'
  shell: docker restart {{ container }}
  arguments:
    - name: container
      type: ascii
```

- use `{{ }}` and give a variable
- under arguments type, assign a type for it, ascii only allows letters and numbers

Execute a shell command with choices

```yaml
- title: Manage Docker Stack Services
  icon: "&#128736;"
  shell: docker-compose -f /home/karis/docker/bookstack/docker-compose.yml {{ action }}
  arguments:
    - name: action
      choices:
        - title: Start Stack
          value: up -d

        - title: Stop Stack
          value: down
```

This example give choices to start or stop a docker stack of a docker-compose file. If a argument is given the parameter choices, it will be in dropdown mode.

### Icons Customization

The icons need to be placed in a folder in */var/www/\[icon-folder\]/icon.png.* To use the icons, offline image or web address, it should be in HTML format. The size of 48px is the default size of OliveTin icons. Other CSS options such as `<em>style="background-color: white;"</em>` also works.

```yaml
icon: '<img src = "icons/minecraft.png" size="48px" />'
```

Icon with emoji, to use emoji, need to use the html code. [https://symbl.cc/en/emoji/](https://symbl.cc/en/emoji/)

For example, `&#9786;` <span class="symbol-main__title--symbl">😊.</span>

```yaml
icon: "&#9786;"
```

#### Icon Management

The default icon folder is `/var/www/olivetin/icons`

The icon folder of all homelab icons is in `~/icons/homelab`

### API

Simple action button.

```bash
curl -X POST "http://mediaserver:1378/api/StartAction" -d '{"actionName": "Update Music"}'
```

Action with Arguments.

```bash
curl -X POST 'http://mediaserver:1378/api/StartAction' -d '{"actionName": "Rename Movies", "arguments": [{"name": "path", "value": "value"}]}'
```