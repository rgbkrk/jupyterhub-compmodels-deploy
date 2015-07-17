FROM jupyter/systemuser

# Install nbgrader
RUN pip2.7 install nbgrader

# Install terminado
RUN pip2.7 install terminado
RUN pip3.4 install terminado

# Create nbgrader profile and add nbgrader config
ADD nbgrader_config.py /etc/ipython/nbgrader_config.py
