Pipenv
======

Pipenv is a tool that makes it easy to distribute the dependencies for a project. It's recommended by the Python Software
Foundation as the best way to solve this problem. We'll be using it in all of our code jams, so it would be a good idea
to try to get used to it.

Requirements
------------

Pipenv itself requires the following to be installed:

* Python 3, installed with the "Add to PATH" option enabled if you're on Windows
* Pip, which should be installed alongside Python on Windows, but may need to be installed separately on other platforms
* Optionally, Pyenv - this allows Pipenv to install the needed version of Python for you as well, in the event that you don't have it

Once you have the necessary requirements, you can open a terminal or command prompt and run `pip install pipenv` to get Pipenv installed.

Using Pipenv
------------

Pipenv is usually used from a terminal or command prompt. Open a terminal in the project directory, or use `cd path/to/project` to move there
in an already-opened terminal. From there, the following commands are available:

* `pipenv sync --dev` will install all of the needed dependencies for you, into a virtual environment
* `pipenv install <package>` will install a `package` to your virtual environment and update the `Pipfile` and `Pipfile.lock` accordingly
* `pipenv uninstall <package>` will remove an installed `package` from your virtual environment and update the `Pipfile` and `Pipfile.lock` accordingly
* `pipenv run <command>` will run a `command` using your virtual environment - for example, `pipenv run <filename>` will run `filename` using the Python in your virtual environment
* `pipenv shell` will open up a Python shell using the Python in your virtual environment

As a first step, you should run `pipenv sync --dev` to set up your environment. You will also need to run this again if a teammate updates the
`Pipfile` or `Pipfile.lock` - for example, if they add a new package to it, or remove an old one.

Pipenv And You
--------------

Pipenv is best-used from a terminal or command prompt. However, the virtual environments it creates act like any others, and it is possible to use them
in your editor or IDE to run or debug your project. Visual Studio Code [supports PyEnv natively](https://code.visualstudio.com/docs/python/environments), 
but editors that don't provide an integration will have to be set up manually. Fortunately, doing that is usually quite simple.

When you first run `pipenv sync`, it tells you where the virtual environment it creates is located. For example, it may be located in
`/home/username/.virtualenvs/code-jam-1-FgMl5Zkj`. The Python interpreter for the virtual environment is located within it, in `Scripts/python`,
or `Scripts/python.exe` if you're on Windows.

All you need to do is add this interpreter to your editor, using its configuration tools. In our example, the interpreter is located at
`/home/username/.virtualenvs/code-jam-1-FgMl5Zkj/Scripts/python`, so that is what you'd add to your editor.

The Pipenv documentation maintains [a list of community-supported integrations](https://docs.pipenv.org/advanced/#community-integrations).
If your editor is not listed there, you'll need to set up manually. Please refer to the documentation for your editor for more information on
how to do this.

---

**Make sure you use Pipenv** - if you do not, your dependencies won't be available to your project.

If you get stuck, don't be afraid to ask for help on the server - but please do take a stab at this yourself first!