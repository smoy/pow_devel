#
# super simple ci/cd with invoke ;)
# 
# invoke docs = http://docs.pyinvoke.org/en/1.2/getting-started.html
#       specific: change workdir: https://github.com/pyinvoke/invoke/issues/225

from invoke import task
import os,sys
import argparse

@task(help={'name': "Name of the test application. Default = testapp"})
def build(c, path="../..", name="testapp"):
    """
        Create a testapp from the current git version
            generate_app -n <name> -p <path>
        create the according venv
            cd (abspath)
            virtrualenv venv
        activate the pip environment
            win: venv\Scripts\activate
            other: source venv/bin/activate
        install the requirements
            pip install -r requirements.txt
        run the tests
            cd tests
            python runtests
        run the server
            python server.py
        
        => You can find the testresults here:
            localhost:8080/testresults
    """
    if not os.name in ["nt", "posix"]:
        print("Sorry. this only supports Posix (e.g. Linux, OSX) and Windows OS. ")
        sys.exit()

    path=os.path.normpath(path)
    print("Building : -n {} -p {} ".format(name, path))
    if os.path.exists(os.path.join(path, name)):
        print("sorry, path {} exists".format(os.path.abspath(os.path.join(path, name))))
        r=input(" .. type y or yes, to go ahead deleting the existing: {} ? : ".format(os.path.join(path,name)))
        if r in ["y", "yes"]:
            import shutil
            r=shutil.rmtree(os.path.join(path,name))
            print(40*"-")
            print(" ..... deleted dir tree: {}".format(os.path.join(path, name)))
            print(40*"-")
            build_all(c,name, path)
        else:
            print(40*"-")
            print(" ok, exiting...")
            print(40*"-")
            sys.exit()
    else:
        # start the build and check
        build_all(c,name, path)




def build_all(c, name, path, force=False):
    """
        the actual function that does the job
    """
    print(40*"-")
    print(" starting the build and check...")
    print(40*"-")
    # genate the app
    if force:
        r=c.run("python generate_app.py -n {} -p {} -f".format(name, path))
    else:
        r=c.run("python generate_app.py -n {} -p {}".format(name, path))
        
    print(" .. generated the PythonOnWheels app.")
    # switch the current dir for invoke. every c.run starts from that dir.
    app_path=os.path.abspath(os.path.join(path, name))
    # create a venv
    if os.name == "nt":
        with c.cd(app_path):
            print(" .. creating a virtualenv")
            c.run("python -m venv ./venv")
            print(" .. Installing the PoW requirements")
            c.run("cd ./venv/Scripts && pip.exe install -r {}".format(
                os.path.normpath(os.path.join("..\..", "requirements.txt"))))
    elif os.name == "posix":
        with c.cd(app_path):
            print(" .. creating a virtualenv")
            c.run("python -m venv ./venv")
        with c.cd(os.path.join(app_path, "venv/bin")):
            print(" .. Installing the PoW requirements")
            print("cwd: " + c.cwd)
            #pipath= os.path.abspath(os.path.join(app_path, "./venv/bin/pip"))
            #print("venv pip path: {}".format( pipath ))
            reqpath = os.path.normpath(os.path.join( app_path, "requirements.txt"))
            print("requirements.txt: {}".format(reqpath))
            c.run("./pip install -r {}".format( reqpath ))
            c.run("./pip freeze")
    else:
        print("only posix and windows compatible OS are supported, sorry!")
        sys.exit()
    test(c,path,name)
    runserver(c,path,name)

@task
def test(c,  path="../..", name="testapp"):
    path=os.path.normpath(path)
    app_path=os.path.abspath(os.path.join(path, name))
    print("app_path: " + app_path)
    with c.cd(os.path.join(app_path, "tests")):
        if os.name == "nt":
            print("cwd: " + c.cwd)
            print(" .. running the tests .. ")
            pypath=os.path.normpath(os.path.join(app_path,"./venv/Scripts/python.exe"))
            print("pyhton.exe path:" + pypath)
            c.run("{} runtests.py".format(pypath))
        elif os.name == "posix":
            print("cwd: " + c.cwd)
            print(" .. running the tests .. ")
            pypath=os.path.normpath(os.path.join(app_path,"./venv/bin/python"))
            print("pyhton path:" + pypath)
            c.run("{} runtests.py".format(pypath))
        else:
            print("only posix and windows compatible OS are supported, sorry!")
            sys.exit()

@task
def runserver(c, path="../..", name="testapp"):
    path=os.path.normpath(path)
    app_path=os.path.abspath(os.path.join(path, name))
    print("app_path: " + app_path)
    with c.cd(app_path):
        if os.name == "nt":
            print(" .. starting the server .. ")
            print(" .. check testresults at: localhost:8080/testresults")
            pypath=os.path.normpath(os.path.join(app_path,"./venv/Scripts/python.exe"))
            c.run("{} server.py".format(pypath))
        elif os.name == "posix":
            print(" .. starting the server .. ")
            print(" .. check testresults at: localhost:8080/testresults")
            pypath=os.path.normpath(os.path.join(app_path,"./venv/bin/python"))
            c.run("{} server.py".format(pypath))
        else:
            print("only posix and windows compatible OS are supported, sorry!")
            sys.exit()
        

@task
def clean(c, path="../..", name="testapp", force=False):
    app_path=os.path.abspath(os.path.normpath(os.path.join(path,name)))
    r=input(" deleting the existing: {} ? Type: y | yes: ".format(app_path))
    if r in ["y", "yes"]:
        import shutil
        r=shutil.rmtree(os.path.join(path,name))
        print(40*"-")
        print(" ..... deleted dir tree: {}".format(app_path))
        print(40*"-")

@task
def versiontest(c, nocache=False, path=".."):
    """
        - build the current wheel / dist
        - run the container (image: pow-ubuntu-python-versiontest) with mounted dist volume
        - container runs tests automatically
    """
    import glob
    import os
    import shutil
    with c.cd(os.path.normpath(path)):
        print(40*"-")
        print(" Preparing the multi python version test (3.6, 2.7, 3.8) ")
        print(40*"-")
        cache = not nocache
        print(f" using docker cache: {cache}")
        print(" building the framework....")
        # deleting old releases.
        c.run("rm -rf ./build/*")
        # build the framework
        c.run("python setup.py -q sdist bdist_wheel")
        print(" done.")
    with c.cd(os.path.normpath("../testcontainer")):
        #get lastest wheel filename
        list_of_files = glob.glob("../dist/*.whl") # * means all if need specific format then *.csv
        latest_file = os.path.basename(max(list_of_files, key=os.path.getctime))
        print(f" using: {latest_file}")
        print(f" building the test container image...")
        r=shutil.copy(f"../dist/{latest_file}", "./pow.whl")
        if nocache:
            c.run(f"docker build --no-cache --build-arg POW_WHEEL={latest_file} -t powversiontest .")
        else:
            c.run(f"docker build --build-arg POW_WHEEL={latest_file} -t powversiontest .")
    pass

@task
def testcliparams(c, name="def"):
    """
        handing over cli arguments using --parameter_name=value
        try:
                invoke test --name="somethingelse"
    """
    print(name)
