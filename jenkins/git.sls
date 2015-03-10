{% set jenkins = pillar.get('jenkins', {}) -%}
{% set home = jenkins.get('home', '/usr/local/jenkins') -%}
{% set user = jenkins.get('user', 'jenkins') -%}
{% set group = jenkins.get('user', user) -%}
{% set git = jenkins.get('git', {}) -%}
{% set git_hosts = git.get('hosts', []) -%}

dotssh_dir:
  file.directory:
    - name: {{ home }}/.ssh
    - mode: 0700
    - user: {{ user }}
    - group: {{ group }}

git_key:
  file.managed:
    - name: {{ home }}/.ssh/id_rsa_git
    - contents_pillar: jenkins:git:prvkey
    - mode: 0600
    - user: {{ user }}
    - group: {{ group }}

{% for host in git_hosts -%}
git_host_{{ host }}_known:
  ssh_known_hosts.present:
    - name: {{ host }}
    - user: {{ user }}

git_host_{{ host }}_setup:
  file.append:
    - name: {{ home }}/.ssh/config
    - text: |
        Host {{ host }}
             Identityfile ~/.ssh/id_rsa_git
{%- endfor %}