{% set jenkins = pillar.get('jenkins', {}) -%}
{% set home = jenkins.get('home', '/usr/local/jenkins') -%}

include:
  - jenkins.cli.uninstall
  - jenkins.plugins.uninstall
  - supervisor.uninstall
  - python.uninstall

remove_site:
  file.absent:
    - name: /etc/nginx/sites-available/jenkins.conf

remove_site_link:
  file.absent:
    - name: /etc/nginx/sites-enabled/jenkins.conf

remove_pkgs:
  pkg.purged:
    - pkgs:
      - jenkins
      - nginx-full

remove_user:
  user.absent:
    - name: jenkins

remove_home:
  file.absent:
    - name: {{ home }}
