from setuptools import setup


setup()


# from setuptools import find_packages
# # or
# from setuptools import find_namespace_packages

# from mxdataset import __version__

# VERSION = __version__


# with open("README.md") as f:
#     LONG_DESCRIPTION = f.read()


# setup(
#     name="mxdataset_devkit",
#     version=VERSION,
#     description="A mxdataset devkit.",
#     long_description=LONG_DESCRIPTION,
#     long_description_content_type="text/markdown",
#     author="zwx",
#     author_email="zwxdlut@163.com",
#     license = "GPLv3",
#     url="https://github.com/user/repo",
#     # project_urls={
#     #     "Documentation": "https://flask.palletsprojects.com/",
#     #     "Code": "https://github.com/pallets/flask",
#     #     "Issue tracker": "https://github.com/pallets/flask/issues",
#     #     },
#     classifiers=[
#         "Development Status :: 3 - Alpha",
#         "Environment :: Console",
#         "Framework :: Flask",
#         "Intended Audience :: Developers",
#         "License :: OSI Approved :: GPLv3 License",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python :: 3",
#         "Topic :: Software Development :: Libraries :: Python Modules",
#         ],
#     zip_safe=False,
#     packages=find_packages(
#         # where='src',
#         # include=['pkg*'],  # alternatively: `exclude=['additional*']`
#         ),
#     # packages=['mypkg', 'mypkg.subpkg1', 'mypkg.subpkg2']
#     # packages=find_namespace_packages(where='src'),
#     # package_dir = {
#     #     "": "src"  # directory containing all the packages (e.g.  src/mypkg, src/mypkg/subpkg1, ...)
#     #     "mypkg": "lib",  # mypkg.module corresponds to lib/module.py
#     #     "mypkg.subpkg1": "lib1",  # mypkg.subpkg1.module1 corresponds to lib1/module1.py
#     #     "mypkg.subpkg2": "lib2",  # mypkg.subpkg2.module2 corresponds to lib2/module2.py
#     #     }
#     # namespace_packages=['timmins']
#     include_package_data=True,
#     # package_data={
#     #     # 引入任何包下面的 *.txt、*.rst 文件
#     #     "": ["*.txt", "*.rst"],
#     #     # 引入 hello 包下面的 *.msg 文件
#     #     "hello": ["*.msg"],
#     #     },
#     # # 不引入 README.txt 文件
#     # exclude_package_data={"": ["README.txt"]},
#     data_files=[
#         # ("", ["conf/*.conf"]),
#         # ("/usr/lib/systemd/system/", ["bin/*.service"]),
#         ("", ["config/mxdataset.yaml"]),
#         ],
#     entry_points={
#         "console_scripts": [
#             # "foo = my_package.some_module:main_func",
#             "migrate = mxdataset.migration.migration:migrate"
#             ],
#         # "gui_scripts": [
#         #     "baz = my_package_gui:start_func",
#         #     ]
#     },
#     python_requires=">=3.8",
#     install_requires=[
#         "requests",
#         "pyyaml",
#         "boto3",
#         "lakefs_client @ git+http://192.168.70.202:30453/ai-model/lakefs_client.git@master",
#         "pycocotools>=2.0.6",
#         ],
#     # extras_require={
#     #     "dotenv": ["python-dotenv"],
#     #     "dev": [
#     #         "pytest",
#     #         "coverage",
#     #         "tox",
#     #         "sphinx",
#     #         "pallets-sphinx-themes",
#     #         "sphinxcontrib-log-cabinet",
#     #         "sphinx-issues",
#     #         ],
#     #     "docs": [
#     #         "sphinx",
#     #         "pallets-sphinx-themes",
#     #         "sphinxcontrib-log-cabinet",
#     #         "sphinx-issues",
#     #         ],
#     #     },
#     dependency_links=[
#         "https://pypi.python.org/simple",
#         "https://pypi.tuna.tsinghua.edu.cn/simple/",
#         ],
# )
