FROM ipython/scipystack

# Install nbgrader
RUN pip2.7 install git+git://github.com/jupyter/nbgrader.git@master

# Add nbgrader config
ADD nbgrader_config.py /etc/ipython/nbgrader_config.py

# Switch to the right directory and run the formgrader
WORKDIR /home/jhamrick/class_files
CMD ["nbgrader", "formgrade", "--log-level=10"]
