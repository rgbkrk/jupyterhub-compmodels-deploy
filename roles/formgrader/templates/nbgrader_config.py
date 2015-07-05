c = get_config()

c.NbGraderConfig.course_id = 'cogsci131'
c.FormgradeApp.ip = "127.0.0.1"
c.FormgradeApp.port = 9000
c.FormgradeApp.authenticator_class = "nbgrader.auth.hubauth.HubAuth"
c.HubAuth.graders = ["jhamrick"]
c.HubAuth.notebook_url_prefix = "class_files"
c.HubAuth.hubapi_address = "{{ servicenet_ip }}"
c.HubAuth.hub_base_url = "https://compmodels.tmpnb.org"
