c = get_config()

c.NbGraderConfig.course_id = '{{ course_id }}'

c.FormgradeApp.ip = "127.0.0.1"
c.FormgradeApp.port = 9000
c.FormgradeApp.authenticator_class = "nbgrader.auth.hubauth.HubAuth"

c.HubAuth.notebook_url_prefix = "{{ nbgrader_root }}"
c.HubAuth.hubapi_address = "{{ servicenet_ip }}"
c.HubAuth.hub_base_url = "{{ hub_base_url }}"

# Add users to the grader list
graders = set(["{{ nbgrader_user }}"])
with open('/etc/ipython/graderlist') as f:
    for line in f:
        if line.isspace():
            continue
        graders.add(line.strip())
c.HubAuth.graders = list(graders)
